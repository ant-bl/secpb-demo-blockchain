#!/usr/bin/env python3

import argparse
import json
import logging
import socket


def do_run(path: str, socket_path: str):
    with open(path, "r") as in_:
        fingerprint = json.load(in_)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        logging.info(f"Connecting to {socket_path}")
        client.connect(socket_path)
        data = json.dumps(fingerprint).encode("utf8")
        logging.info(f"Sending to {data}")
        client.sendall(data)


def main():
    parser = argparse.ArgumentParser("Imitate a VM that has migrate and send a fingerprint through a unix socket to a "
                                     "blockchain")

    parser.add_argument("--path", help="path that contains the fingerprint", required=True)
    parser.add_argument("--socket-path", help="socket path of the blockchain", required=True)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    do_run(args.path, args.socket_path)


if __name__ == "__main__":
    main()
