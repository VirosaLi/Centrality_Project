from bs4 import BeautifulSoup
from networkx import DiGraph, nx_agraph
from networkx.algorithms import *
import networkx as nx
from graphcommons import GraphCommons, Signal
import requests
import json
from urllib.parse import unquote
import matplotlib.pyplot as plt

dep_selector = "#dependencies > ul:nth-child(2) > li > a"
dev_selector = "#dependencies > ul:nth-child(4) > li > a"

access_token = 'sk_2ehhdwcavoaogh7EfldMNA'


def url_formatter(page_name):
    return f"https://www.npmjs.com{page_name}?activeTab=dependencies"


def import_package_dependencies(package, dependencies_dict, max_depth=3, depth=0):
    """
    recursively import dependencies and sub dependencies of a node module from npm website

    :param package: package name
    :param dependencies_dict: a dictionary that hold all the result
    :param max_depth: the dependency depth bound
    :param depth: current depth
    :return: none
    """
    # base case. return when the current package is already in the dict or the depth is greater than max
    if package in dependencies_dict or depth > max_depth:
        return

    # request the html of the package's npm page
    page = requests.get(url_formatter(package))

    # create soup and select the dependencies using CSS selector
    soup = BeautifulSoup(page.content, 'html.parser')
    dependencies = soup.select(dep_selector)

    # decode package name from url form
    dependencies_list = [unquote(dep['href']) for dep in dependencies]

    # add the dependencies list to the dict
    dependencies_dict[package] = dependencies_list

    # recursively call itself to import all dependencies
    for dep in dependencies_list:
        import_package_dependencies(dep, dependencies_dict, depth=depth + 1)


def build_graph_from_dict(graph, dependencies_dict):
    """

    :param graph:
    :param dependencies_dict:
    """
    for package, dep_list in dependencies_dict.items():
        package = package.replace('/package/', '')
        graph.add_node(package, type='package')
        for dep in dep_list:
            dep = dep.replace('/package/', '')
            graph.add_node(dep, type='package')
            graph.add_edge(package, dep, type='depends on')


def create_graph_visualization(graphcommons_client, graph, package_name):
    """
    create a graph on the graph commons website.

    :param graphcommons_client: graph commons client
    :param graph: a networkX graph
    :param package_name: package name
    :return: the graph id
    """
    signals = []
    for node, data in graph.nodes(data=True):
        signal = Signal(action="node_create", name=node, type=data['type'], reference=url_formatter(node))
        signals.append(signal)

    for source, target, data in graph.edges(data=True):
        signal = Signal(
            action="edge_create", from_name=source, from_type=graph.node[source]['type'],
            to_name=target, to_type=graph.node[target]['type'], name=data['type'], weight=1
        )
        signals.append(signal)

    print("number of signals: ", len(signals))

    created_graph = graphcommons_client.new_graph(
        name=f"Dependency Network of {package_name}",
        description=f"Dependency Network of {package_name} Package",
        signals=signals
    )

    return created_graph.id


def eigenvector_centrality_of_graph(graph):
    """
    calculate betweenness centrality of a networkx digraph.

    :param graph: a networkx Digraph
    :return: a sorted dictionary of betweenness centrality in descending order
    """
    bitw_dict = eigenvector_centrality(graph)
    sorted_dict = sorted(bitw_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_dict


def betweenness_centrality_of_graph(graph):
    """
    calculate betweenness centrality of a networkx digraph.

    :param graph: a networkx Digraph
    :return: a sorted dictionary of betweenness centrality in descending order
    """
    bitw_dict = betweenness_centrality(graph)
    sorted_dict = sorted(bitw_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_dict


def closeness_centrality_of_graph(graph):
    """
    calculate closeness centrality of a networkx digraph.

    :param graph: a networkx Digraph
    :return: a sorted dictionary of betweenness centrality in descending order
    """
    bitw_dict = closeness_centrality(graph)
    sorted_dict = sorted(bitw_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_dict


def degree_centrality_of_graph(graph):
    """
    calculate closeness centrality of a networkx digraph.

    :param graph: a networkx Digraph
    :return: a sorted dictionary of betweenness centrality in descending order
    """
    bitw_dict = degree_centrality(graph)
    sorted_dict = sorted(bitw_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_dict


def from_json_to_dot(json_path, dot_name):

    with open(json_path, 'r') as data_file:
        json_data = json.load(data_file)

        # build dependency graph
        graph = DiGraph()
        build_graph_from_dict(graph, json_data)

        # write graph to dot file
        py_graph = nx_agraph.to_agraph(graph)
        py_graph.write(dot_name)


def test():
    package_name = "/package/web3"
    dependency_tree_depth = 5

    # import package dependencies
    dependencies_dict = {}
    import_package_dependencies(package_name, dependencies_dict, dependency_tree_depth, 0)

    # print out dependency dictionary
    for k, v in dependencies_dict.items():
        print(k, v)

    # build graph from dependency dict
    graph = DiGraph()
    build_graph_from_dict(graph, dependencies_dict)

    # create graph on graph commons
    graphcommons_client = GraphCommons(access_token)
    package_name = package_name.replace('/package/', '')
    graph_id = create_graph_visualization(graphcommons_client, graph, package_name)
    print('graph id:', graph_id)


def main():

    data = 'dependencies_data.json'

    with open(data, 'r') as data_file:
        json_data = json.load(data_file)

        for package, dependencies in json_data.items():
            print(package, dependencies)

        # build dependency graph
        graph = DiGraph()
        build_graph_from_dict(graph, json_data)

        # create graph on graph commons
        graphcommons_client = GraphCommons(access_token)
        graph_id = create_graph_visualization(graphcommons_client, graph, "300 Starts")
        print('graph id:', graph_id)

        # bt_list = closeness_centrality_of_graph(graph)
        #
        # c = 0
        # for t in bt_list:
        #     if t[1] != 0.0 and c < 30:
        #         print(t)
        #         c = c + 1

        # py_graph = nx_agraph.to_agraph(graph)

        # pos = nx.spring_layout(graph, iterations=100)

        # pos = nx.circular_layout(graph)
        #
        # plt.figure()
        #
        # nx.draw(graph, pos)
        #
        # plt.show()


if __name__ == '__main__':
    main()
    # test()
