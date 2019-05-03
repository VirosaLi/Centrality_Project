import time
import requests

import pandas as pd


class Client:

    base_url = "https://api.etherscan.io/api"

    def __init__(self, api_key):
        self.API_KEY = api_key
        self.session = requests.session()

    def send_request(self, payload):
        try:
            req = self.session.get(self.base_url, params=payload)
        except requests.exceptions.ConnectionError:
            raise Exception

        if req.status_code == 200:
            return req.json()
        else:
            return 1

    def current_block_number(self):
        """
        get the current block number.
        :return: current block number
        """
        payload = {"module": "proxy",
                   "action": "eth_blockNumber",
                   "apikey": self.API_KEY}
        res_json = self.send_request(payload)
        return int(res_json['result'], 16)

    def get_block_transaction_count_by_number(self, block_number):
        """
        get the transaction count of a block
        :param block_number: block number
        :return: transaction count
        """
        payload = {"module": "proxy",
                   "action": "eth_getBlockTransactionCountByNumber",
                   "tag": hex(block_number),
                   "apikey": self.API_KEY}
        res_json = self.send_request(payload)
        return int(res_json['result'], 16)

    def get_transaction_by_block_number_and_index(self, block_number, tx_index):
        """
        get a transaction at an index position of a block
        :param block_number:
        :param tx_index:
        :return: transaction
        """
        payload = {"module": "proxy",
                   "action": "eth_getTransactionByBlockNumberAndIndex",
                   "tag": hex(block_number),
                   "index": hex(tx_index),
                   "apikey": self.API_KEY}
        return self.send_request(payload)

    def get_internal_transaction_by_hash(self, tx_hash):
        """
        get all internal transactions of one normal transaction
        :param tx_hash: transaction hash of a normal transaction
        :return: result that contains a list of internal transactions
        """
        payload = {"module": "account",
                   "action": "txlistinternal",
                   "txhash": tx_hash,
                   "apikey": self.API_KEY}
        return self.send_request(payload)

    def get_internal_transaction_by_block(self, block_number):
        """
        get all internal transactions of a block
        :param block_number:
        :return:
        """

        # TODO handle exception
        tx_list = []
        num_tx = self.get_block_transaction_count_by_number(block_number)
        for i in range(num_tx):
            tx_json = self.get_transaction_by_block_number_and_index(block_number, i)
            if tx_json['result'] is None:
                continue

            tx_hash = tx_json['result']['hash']

            tx_list_json = self.get_internal_transaction_by_hash(tx_hash)
            if tx_list_json['result'] is None:
                continue

            tx_list.extend(tx_list_json['result'])

        return tx_list

    def get_internal_transaction_by_block_range(self, min_block, max_block):
        """
        get all internal transactions or blocks in a range
        :param min_block:
        :param max_block:
        :return:
        """
        result_list = []
        for i in range(min_block, max_block):
            result_list.extend(self.get_internal_transaction_by_block(i))
            print("block ", i, " finished.\n")
            time.sleep(60)
        return result_list


def test():
    apikey = "CC1BRSEUT5YX8AFQUJJ9HZB4VY69FAG3N3"
    client = Client(apikey)

    curr_block = client.current_block_number()
    list_tx = client.get_internal_transaction_by_block_range(curr_block - 500, curr_block)
    # print(list_tx)
    # print(len(list_tx))

    # tx_list = get_internal_transaction_by_block(curr_block)

    df = pd.DataFrame(list_tx)

    df.to_pickle('./test3.pkl')

    print(df)

    print(df.size)


if __name__ == '__main__':
    test()
