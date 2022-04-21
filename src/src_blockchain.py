#!/usr/bin/env python3

import argparse
import json
import logging
import os
from pathlib import Path
from socketserver import BaseRequestHandler, UnixStreamServer

import asset
import connection as connect


class BlockchainSender:

    def __init__(self, name, port, password=None):

        self.addresses = []
        self.asset_name = "SECPB"
        self.quantity = 1000000
        self.blockchain_port = port
        self.chain_name = name
        self.password = password
        self._asset_pt = None
        self._access_chain_one = None

    def __enter__(self):
        self.connect(self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def connect(self, password):
        logging.info("Connecting with the chain one:")

        pt_chain_one = connect.BlockchainConnect(self.blockchain_port, self.chain_name, password)
        self._access_chain_one = pt_chain_one.start()
        self.addresses.extend(self._access_chain_one.getaddresses())
        if 1 <= len(self.addresses) <= 2:
            self.addresses.extend(self._access_chain_one.getnewaddress())
            logging.info("First address -->", self.addresses[1])

        self._access_chain_one.grant(self.addresses[1], "receive,send")

        self._asset_pt = asset.AssetCreate()
        self._asset_pt.set_asset_params([self.asset_name, True, self.addresses[0], self.quantity])

        try:
            asset_tx_id = self._asset_pt.asset_creation(self._access_chain_one)
        except Exception:
            logging.info("Asset existing !")

    def send(self, fingerprint):

        mem_hash = fingerprint["fingerprint"]["fingerprints"]["memory"]["hash"]
        uuid = fingerprint["fingerprint"]["uuid"]
        encoded_fingerprint = f"vm_dst {self.chain_name} {mem_hash} {uuid}"
        hex_fingerprint = encoded_fingerprint.encode("utf-8").hex()

        logging.info("Data hex is %s", hex_fingerprint)
        res_tx_id = self._asset_pt.sendWithData(self.addresses[1], self._access_chain_one, hex_fingerprint)
        logging.info("Tx ID  %s", str(res_tx_id))


class JSONRequestHandler(BaseRequestHandler):

    def handle(self):

        quit_ = False

        while not quit_:
            js = None
            str_ = ""

            # Wait for a fingerprint
            while not quit_ and js is None:
                raw_recv = self.request.recv(1)

                if len(raw_recv) == 0:
                    quit_ = True
                else:
                    str_ += raw_recv.decode("utf8").strip()

                try:
                    js = json.loads(str_)
                    self.server.request = js
                except json.decoder.JSONDecodeError:
                    pass


class UnixServerQueue(UnixStreamServer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = None

    @property
    def request(self):
        req = self._request
        self._request = None
        return req

    @request.setter
    def request(self, req):
        assert req is not None
        assert self._request is None
        self._request = req


def do_run_file(path: str):
    with open(path, "r") as in_:
        yield json.load(in_)


def do_run_unix_server(path: Path):
    try:
        os.remove(path)
    except OSError:
        pass

    with UnixServerQueue(str(path), JSONRequestHandler) as server:
        try:
            while True:
                server.handle_request()
                req = server.request
                if req is not None:
                    yield req
        finally:
            server.server_close()


def do_run(path: str, name: str, port: str, password: str):
    prefix = "unix:"

    if path.startswith(prefix):
        path = path[len(prefix):]
        fn = do_run_unix_server
    else:
        fn = do_run_file

    with BlockchainSender(name, port, password) as sender:
        for fingerprint in fn(path):
            data = {'fingerprint': fingerprint}
            logging.info(f"get fingerprint : {fingerprint}")
            sender.send(data)


def main():
    parser = argparse.ArgumentParser("Run a server that accepts fingerprint through unix socket and forward it to " +
                                     "an HTPP server through a POST connection.")

    parser.add_argument("--path", help="path that will used to read the fingerprint. If the paths starts by unix: " +
                                       "the fingerprint will be read through a socket unix", required=True)
    parser.add_argument("--chain-name", help="The name of Blockchain", required=True)
    parser.add_argument("--chain-port", help="Port used by the Blockchain", required=True)
    parser.add_argument("--password", help="password")
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    do_run(args.path, args.chain_name, args.chain_port, args.password)


if __name__ == "__main__":
    main()
