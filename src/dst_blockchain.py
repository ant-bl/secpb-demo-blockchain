#!/usr/bin/env python3


import argparse
import json
import logging
import socket
import time
from pathlib import Path
from typing import Dict

import asset
import blockhandler
import connectionNew as connect


def do_write_fingerprint_unix(socket_path: str, js: Dict):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(socket_path)
        client.send(json.dumps(js, ensure_ascii=True).encode("utf8"))


def do_write_fingerprint_file(path: str, js: Dict):
    with open(path, "w") as out:
        json.dump(js, out)


def do_write_fingerprint(path, js: Dict):
    print("receive_fingerprint:", json.dumps(js, indent=True))

    prefix = "unix:"
    if path.startswith(prefix):
        do_write_fingerprint_unix(path[len(prefix):], js)
    else:
        do_write_fingerprint_file(path, js)


def do_run(path: str, socket_path: str, data_list):
    with open(path, "r") as in_:
        fingerprint = json.load(in_)

    fingerprint["fingerprints"]["memory"]["hash"] = data_list[2]
    fingerprint["uuid"] = data_list[3]

    do_write_fingerprint(socket_path, fingerprint)


class HeightStore:

    def __init__(self, path: Path):
        self._path = path

        try:
            self.load()
        except FileNotFoundError:
            self.save(0)

    def load(self):
        with self._path.open('r') as file:
            height = file.read()
            return int(height)

    def save(self, height):
        with self._path.open('w') as file:
            file.write(str(height))


def recv_data(data_to_send, template_path, socket_path):
    for item in data_to_send:
        try:
            if isinstance(item, dict):
                pass
            else:
                decoded = bytes.fromhex(item).decode('utf-8')
                data_list = decoded.split(" ")
                print("Received data", data_list)
                if data_list[0] == "vm_dst":
                    do_run(template_path, socket_path, data_list)
        except UnicodeDecodeError:
            pass


def main():
    parser = argparse.ArgumentParser("Run a server that accepts fingerprint through unix socket and forward it to " +
                                     "an HTPP server through a POST connection.")

    parser.add_argument("--chain-name", help="The name of Blockchain", required=True)
    parser.add_argument("--chain-port", help="Port used by the Blockchain", required=True)
    parser.add_argument("--password", help="password")
    parser.add_argument("--socket-path", help="socket path to reach vm dest", required=True)
    parser.add_argument("--template-path", help="template path", required=True)
    parser.add_argument("--polling-time", help="time between two polls in seconds", default=2)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    print("Starting with the chain One:  \n")
    pt_chainOne = connect.BlockchainConnect(args.chain_port, args.chain_name, args.password)
    access_chainOne = pt_chainOne.start()
    asset_pt = asset.AssetCreate()
    handler = blockhandler.BlockHandler(access_chainOne)

    height_store = HeightStore(Path("height.dat"))

    last_height = height_store.load()
    print("Last height value", last_height)
    while True:

        try:
            height = handler.retrieveBlockheight(access_chainOne)
            # print(" Block  height retrieved !")
            print("Height: ", height, "Last height: ", last_height)
            if height > last_height:
                for i in range(last_height, (height + 1)):
                    block = handler.getBlock(access_chainOne, i)
                    data = handler.explore_block(block)
                    recv_data(data, args.template_path, args.socket_path)
                last_height = height

            time.sleep(args.polling_time)

        finally:
            height_store.save(height)


if __name__ == '__main__':
    main()