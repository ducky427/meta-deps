
import re
import sys
import tarfile
import xmlrpclib

from cStringIO import StringIO

import requests
import requests_cache
requests_cache.install_cache()


def _extract_deps(content):
    """ Extract dependencies using install_requires directive """
    results = re.findall("install_requires=\[([\W'a-zA-Z0-9]*?)\]", content, re.M)
    deps = []
    if results:
        deps = [a.replace("'", "").strip()
                for a in results[0].strip().split(",")
                if a.replace("'", "").strip() != ""]
    return deps


def _extract_setup_content(package_file, name):
    """Extract setup.py content as string from downladed tar """
    tar_file = tarfile.open(fileobj=package_file)
    setup_candidates = [elem for elem in tar_file.getmembers() if 'setup.py' in elem.name]

    if len(setup_candidates) >= 1:
        a = [elem.name for elem in setup_candidates]
        setup_member = min(a, key=lambda x:len(x))
        content = tar_file.extractfile(setup_member).read()
        return content
    else:
        print "Too few candidates for setup.py in tar for package: %s" % (name, )
        return ''


def get_package_data(name):
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    releases = client.package_releases(name)
    if not releases:
        return

    release = releases[0]

    doc = [d for d in client.release_urls(name, release) if 'url' in d and '.tar' in d['filename']]
    if not doc:
        return

    urls = [d.get('url') for d in doc if d.get('url')]
    url = min(urls, key=lambda x:len(x))

    #print "Downloading url %s" % url
    req = requests.get(url)
    if req.status_code != 200:
        print "Could not download file %s. URL: %s" % (req.status_code, url)
        return

    tar_file = StringIO()
    tar_file.write(req.content)

    result_tar_file = StringIO(tar_file.getvalue())

    try:
        content = _extract_setup_content(result_tar_file, name)
        deps = [d for d in _extract_deps(content) if '#' not in d]
    except Exception as inst:
        print inst, url
        print "Unexpected error:", sys.exc_info()[0]
        deps = []

    return [name, release, deps]
