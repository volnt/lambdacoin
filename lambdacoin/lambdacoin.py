# -*- coding: utf-8 -*-
import argparse

from flask import Flask, request, make_response, jsonify

from .wallet import Wallet
from .node import Node


def wallet(args):
    print u"ƛ λCoin Wallet ƛ"
    if args.generate:
        print "Generate wallet key pair :"
        wallet = Wallet()
    elif args.private_key:
        print "Load wallet key pair :"
        with open(args.private_key) as f:
            private_key = f.read()

        wallet = Wallet(private_key=private_key)

    print """
Public key:
{}

Private key:
{}""".format(wallet.public_key, wallet.private_key)


def node(args):
    app = Flask(__name__)
    node = Node(u"localhost:{}".format(args.port))

    @app.route('/', methods=['POST'])
    def receive():
        response = node.receive(request.json)

        return make_response(jsonify(response))

    app.run(host="0.0.0.0", port=int(args.port), debug=True)

def miner(args):
    pass


MODULES = {
    "wallet": wallet,
    "node": node,
    "miner": miner,
}


def main():
    parser = argparse.ArgumentParser(description="λCoin client.", add_help=False)

    subparsers = parser.add_subparsers(help="subcommand help")

    wallet_parser = subparsers.add_parser("wallet", help="λWallet")
    wallet_group = wallet_parser.add_mutually_exclusive_group(required=True)
    wallet_group.add_argument("--generate", action="store_true",
                              help="Generate a new key pair.")
    wallet_group.add_argument("private_key", nargs='?', help="Wallet private key")
    wallet_parser.set_defaults(func=wallet)

    miner_parser = subparsers.add_parser("miner", help="λMiner")
    miner_parser.set_defaults(func=miner)

    node_parser = subparsers.add_parser("node", help="λNode")
    node_parser.add_argument("--port", type=int, default=6400,
                             help="The node port.")
    node_parser.set_defaults(func=node)

    args = parser.parse_args()
    return args.func(args)
