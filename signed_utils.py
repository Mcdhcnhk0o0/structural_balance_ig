# encoding: utf-8


import collections
# import numpy as np
# import networkx
# import matplotlib.pyplot


"""
Data structures and some common methods are defined here.
1. Data structure for datasets.
2. Read data from a local file.
3. Convert between solution vectors and partitions.
4. Organize partitions into standard formats.
5. Others...
"""


class Dataset:
    """
    data structure for a given dataset

    vnum：num of vertices, int
    enum：num of edges, int
    dataset: a graph stored by adjacency table using hash, dict(dict())
    """
    def __init__(self):
        self.vnum = 0
        self.enum = 0
        self.data = None


def load_data(path: str, network_type='signed') -> Dataset:
    """
    read data from a local file

    :param path: file path
    :param network_type: enum {"unsigned", "signed"}
    :return: an instance of class Dataset
    """

    dataset = Dataset()
    data = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    print('Loading data from ' + path)

    with open(path) as f:
        # the first line
        header = f.readline()
        vnum, enum = header.split()
        dataset.vnum, dataset.enum = int(vnum), int(enum)
        # the remaining
        if network_type == 'signed':
            # each line in the file is expected in the form of "n1 n2 attr"
            for each in f:
                n1, n2, attr = each.split()
                if attr != '1' and attr != '-1':
                    continue
                n1, n2 = int(n1), int(n2)
                data[n1][n2] = data[n2][n1] = int(attr)
        elif network_type == 'unsigned':
            # expected form: "n1 n2"
            for each in f:
                n1, n2 = each.split()
                n1, n2 = int(n1), int(n2)
                data[n1][n2] = data[n2][n1] = 1
        else:
            raise TypeError('no such type of network')

    dataset.data = data
    print('Loading complete!')

    return dataset


def load_data_with_start_one(path: str, network_type: str) -> Dataset:
    """
    In some files or programming languages, the index of an array or the number of a node starts from 1.

    """
    dataset = Dataset()
    data = collections.defaultdict(dict)
    with open(path) as f:
        header = f.readline()
        vnum, enum = header.split()
        dataset.vnum, dataset.enum = int(vnum), int(enum)
        if network_type == 'signed':
            for each in f:
                n1, n2, attr = each.split()
                n1, n2 = int(n1)-1, int(n2)-1
                data[n1][n2] = data[n2][n1] = int(attr)
        elif network_type == 'unsigned':
            for each in f:
                n1, n2 = each.split()
                n1, n2 = int(n1)-1, int(n2)-1
                data[n1][n2] = data[n2][n1] = 1
        else:
            raise TypeError('no such type of network')
    dataset.data = data
    return dataset


def partition2solution(partition: dict, vnum: int, solution_type='list') -> dict or np.array:
    """
    convert a partition into a solution vector

    :param solution_type: enum {"array", "dict" or ""}
    :param partition: a dictionary
    :param vnum: number of vertices in the partition
    :return: required solution, default: a list
    """

    solution = [0] * vnum
    for idx, community in partition.items():
        for node in community:
            solution[node] = idx

    if solution_type == 'array':
        print('The support of numpy is removed.')
        return
        # return np.array(solution)
    elif solution_type == 'dict':
        return {i: solution[i] for i in range(vnum)}
    else:
        return solution


def solution2partition(solution: dict or np.array or list) -> dict:
    """
    convert a solution vector into a partition

    :param solution: a solution vector, iterable
    :return: a partition, dict(cluster_id: set())
    """

    partition = collections.defaultdict(set)

    if isinstance(solution, dict):
        for node, comm in solution.items():
            partition[comm].add(node)

#     elif isinstance(solution, np.ndarray):
#         for node, comm in enumerate(solution):
#             if comm not in partition.keys():
#                 partition[comm] = {node}
#             else:
#                 partition[comm].add(node)

    elif isinstance(solution, list):
        for node, comm in enumerate(solution):
            partition[comm].add(node)

    else:
        raise TypeError('Wrong type of solution')

    return partition


def default_initialization(vnum: int) -> (list or dict, dict):
    """
    Initialization: treat each node as an independent cluster

    :param vnum: number of vertices in a network
    :return: a solution vector and a partition
    """

    partition = dict()
    solution = dict(enumerate(list(range(vnum))))
    for i in range(vnum):
        partition[i] = {i}
    return solution, partition


def reform_partition(partition: dict) -> dict:
    """
    let cluster id start from 0

    :param partition: dict(community: list())
    :return: standard format, cluster id starts from 0
    """

    re_partition = dict()
    idx = 0
    for cluster in partition.values():
        re_partition[idx] = cluster
        idx += 1
    return re_partition


def dataset2g(dataset, file_name='generated_dataset'):
    """
    write a generated dataset to a local file

    :param file_name: give the file a name
    :param dataset: an instance of class Dataset
    :return: file_name
    """

    import time
    file_name = file_name + "_" + str(int(time.time())) + ".g"   # add a time stamp

    with open(file_name, 'w') as f:
        f.write(str(dataset.vnum) + '\t' + str(dataset.enum) + '\n')
        for node in dataset.data:
            for nbr, attr in dataset.data[node].items():
                f.write(str(node) + '\t' + str(nbr) + '\t' + str(attr) + '\n')

    print('-> The dataset is write as ' + file_name)
    return file_name


# unnecessary in most cases

# def network_plot(partition: dict, dataset: Dataset):
#     """
#     display a partitioned network, only for small networks
#
#     :param partition: a partition
#     :param dataset: a dataset
#     :return: None
#     """
#
#     g = networkx.Graph()
#     color_set = ['red', 'yellow', 'blue', 'green', 'orange', 'black', 'brown', 'gold', 'olive', 'pink', 'lime']
#     if len(partition) > len(color_set):
#         print('too many communities(', len(partition), '), need more kind of colors->', len(color_set))
#         raise KeyError
#     # the color of nodes and edges
#     node_color = []
#     edge_color = []
#     # colour
#     for idx, comm in enumerate(partition.keys()):
#         for each in partition[comm]:
#             g.add_node(each)
#             node_color.append(color_set[idx % len(color_set)])
#     for node in dataset.data:
#         for nbr, attr in dataset.data[node].items():
#             g.add_edge(node, nbr)
#             if attr == 1:
#                 edge_color.append('black')
#             else:
#                 edge_color.append('red')
#     # display
#     networkx.draw_networkx(g, with_labels=True, node_size=120, font_size=6,
#                            node_color=node_color, edge_color=edge_color)
#     matplotlib.pyplot.show()


def collect_degree_info(dataset: Dataset, neighborhood) -> dict:

    degree = dict()
    for i in range(dataset.vnum):
        pos_degree = len(neighborhood[i]['+'])
        neg_degree = len(neighborhood[i]['-'])
        i_degree = {
            '+': pos_degree,
            '-': neg_degree
        }
        degree[i] = i_degree

    return degree


def check_node_list(vnum, neighbor: dict):

    alone = set()
    isolated = set()

    for i in range(vnum):
        if i not in neighbor.keys():
            alone.add(i)
            continue
        if not neighbor[i]['+']:
            isolated.add(i)

    node_available = set(range(vnum)) - alone - isolated
    return alone | isolated, list(node_available)


def get_mean_and_std(data: list):
    n = len(data)
    mean = sum(data) / n
    std = sum([(x - mean) ** 2 for x in data]) / n
    return mean, std


def get_dataset_info(path):
    dataset_info = {}
    with open(path) as f:
        header = f.readline()
        vnum, enum = header.split()
        dataset_info["vnum"], dataset_info["enum"] = int(vnum), int(enum)
        penum, nenum, zenum = 0, 0, 0
        for each in f:
            n1, n2, attr = each.split()
            if attr == '1':
                penum += 1
            elif attr == '-1':
                nenum += 1
            elif attr == '0':
                zenum += 1
        dataset_info["positive enum"] = penum
        dataset_info["negative enum"] = nenum
        dataset_info['zero enum'] = zenum
        dataset_info['left'] = int(enum) - penum - nenum - zenum
    return dataset_info


def estimate_community_numbers(n):
    import math
    return (n * math.log(n)) ** 0.5


# print(get_dataset_info('datasets/wiki-undirected.g'))
