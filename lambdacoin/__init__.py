import enum
import pymongo

db = pymongo.MongoClient().lambdacoin


class DataType(enum.Enum):
    BLOCK = 'block'
    TRANSACTION = 'transaction'
    REQUEST_NODES = 'request_nodes'
    REQUEST_BLOCKCHAIN = 'request_blockchain'
