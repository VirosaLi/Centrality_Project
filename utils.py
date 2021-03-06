from web3 import Web3
import json
from hexbytes import HexBytes


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


provider = Web3.IPCProvider('~/.ethereum/geth.ipc')

w3 = Web3(provider)

b = w3.eth.getBlock(7480245)

print(b)

#j = dict(b)

#js = json.dumps(j, cls=HexJsonEncoder)

#print(js)


ct = w3.eth.getBlockTransactionCount(7480245)

print(ct)
