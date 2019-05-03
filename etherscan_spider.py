import requests
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import networkx as nx

from npm_spider import betweenness_centrality_of_graph, closeness_centrality_of_graph, degree_centrality_of_graph

apikey = "CC1BRSEUT5YX8AFQUJJ9HZB4VY69FAG3N3"
base_url = "https://api.etherscan.io/api"


def current_block_number():
    payload = {"module": "proxy",
               "action": "eth_blockNumber",
               "apikey": apikey}
    res_json = requests.get(base_url, params=payload).json()
    return int(res_json['result'], 16)


def get_block_transaction_count_by_number(block_number):
    payload = {"module": "proxy",
               "action": "eth_getBlockTransactionCountByNumber",
               "tag": hex(block_number),
               "apikey": apikey}
    res_json = requests.get(base_url, params=payload).json()
    return int(res_json['result'], 16)


def get_transaction_by_block_number_and_index(block_number, tx_index):
    payload = {"module": "proxy",
               "action": "eth_getTransactionByBlockNumberAndIndex",
               "tag": hex(block_number),
               "index": hex(tx_index),
               "apikey": apikey}
    return requests.get(base_url, params=payload).json()


def get_internal_transaction_by_hash(tx_hash):
    payload = {"module": "account",
               "action": "txlistinternal",
               "txhash": tx_hash,
               "apikey": apikey}
    return requests.get(base_url, params=payload).json()


def get_internal_transaction_by_block(block_number):
    tx_list = []
    num_tx = get_block_transaction_count_by_number(block_number)
    for i in range(num_tx):

        tx_json = get_transaction_by_block_number_and_index(block_number, i)
        if tx_json['result'] is None:
            continue

        tx_hash = tx_json['result']['hash']

        tx_list_json = get_internal_transaction_by_hash(tx_hash)
        if tx_list_json['result'] is None:
            continue

        tx_list.extend(tx_list_json['result'])

    return tx_list


def get_internal_transaction_by_block_range(min_block, max_block):

    result_list = []
    for i in range(min_block, max_block):
        result_list.extend(get_internal_transaction_by_block(i))
        print("block ", i, " finished.\n")
        # time.sleep(60)
    return result_list

# def download_internal_transaction(resume_point=None):
#
#     if resume_point is None:


def test():
    df = pd.read_pickle('./test2.pkl')

    print(df)

    non_create = df.loc[df['type'] != 'create']
    source = non_create['from'].tolist()

    target = non_create['to'].tolist()

    edges = pd.DataFrame({
        'source': source,
        'target': target
    })

    g = nx.from_pandas_edgelist(edges)

    print(betweenness_centrality_of_graph(g))

    print(closeness_centrality_of_graph(g))

    print(degree_centrality_of_graph(g))

    # print(nx.number_of_nodes(g))
    # print(nx.number_of_edges(g))
    #
    # pos = nx.spring_layout(g)
    #
    # nx.draw_networkx_nodes(g, pos, node_size=5)
    #
    # nx.draw_networkx_edges(g, pos, alpha=0.5)
    #
    # plt.show()

    # df['blockNumber'] = df['blockNumber'].astype(int)
    # df['contractAddress'] = df['contractAddress'].astype(str)
    # df['value'] = df['value'].astype(float)

    # print(df.head())
    # print(df.info())
    # print(df.dtypes)
    # print(df.loc[0])

    # create = df.loc[df['type'] == 'create']
    #
    # print(create.info())
    #
    # temp = df.loc[df['to'] == '']
    # print(temp.info())
    # print(df['from'].tolist())

    # source = df['from'].tolist()
    #
    # target = df['to'].tolist()
    #
    # # print(source, target)
    #
    # print(source)
    # print(len(source))
    #
    # print(target)
    # print(len(target))
    #
    # edges = pd.DataFrame({
    #     'source': source,
    #     'target': target
    # })
    #
    # g = nx.from_pandas_edgelist(edges)
    #
    # print(nx.number_of_nodes(g))
    #
    # print(nx.number_of_edges(g))


def main():

    # block_number = 1112952
    # get_internal_transaction_by_block(block_number)
    #
    # w = current_block_number()
    #
    # print(w)
    curr_block = current_block_number()
    list_tx = get_internal_transaction_by_block_range(curr_block - 1000, curr_block)
    # print(list_tx)
    # print(len(list_tx))

    # tx_list = get_internal_transaction_by_block(curr_block)

    df = pd.DataFrame(list_tx)

    df.to_pickle('./data_sample.pkl')

    print(df)

    print(df.size)


if __name__ == '__main__':
    test()
    # main()
