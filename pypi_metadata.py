
import cPickle
import xmlrpclib

from multiprocessing import Pool

import networkx as nx

from loaddata import get_package_data

def main():
    # only one api server so we'll use the deutschland mirror for downloading
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    #print get_package_data('numpy')
    #print get_package_data('Django')
    #print get_package_data('scipy')
    #print get_package_data('django-freeplay')

    #1/0
    packages = client.list_packages()

    pool = Pool()
    results = pool.map(get_package_data, packages)
    results_data = filter(None, results)

    with open('pypi-deps.txt', 'wb') as f:
        cPickle.dump(results_data, f, cPickle.HIGHEST_PROTOCOL)


def create_graph():
    data = []
    G = nx.Graph()

    data = cPickle.load('pypi-deps.txt')
    packages = set([d[0] for d in data])

    for ex in data:
        name, version, deps = ex
        G.add_node(name)
        for dep in deps:
            if '#' in dep:
                continue

            if ">" in dep:
                dep = dep.split('>')[0]

            if "=" in dep:
                dep = dep.split('=')[0]
            dep = dep.replace("\"", "").strip()
            if dep not in packages:
                continue

            G.add_edge(name, dep)

    nx.write_gml(G, 'test.gml')
    return G

if __name__ == '__main__':
    main()

