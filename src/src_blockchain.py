#!/usr/bin/env python3

import argparse
import json
import logging
import os
from pathlib import Path
from socketserver import BaseRequestHandler, UnixStreamServer

import to_blockchain as sb


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

    for fingerprint in fn(path):
        data = {'fingerprint': fingerprint}

        logging.info(f"get fingerprint : {fingerprint}")

        sb.Send_to_blockchain(name, port, data, password)


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
