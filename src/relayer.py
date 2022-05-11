#!/usr/bin/env python3

import argparse
import json
import logging
import time
from pathlib import Path

import asset
import blockhandler
import connection as connect
import settings
from height_store import HeightStore


def get_fingerprint(template_path: Path, item):
    with template_path.open("r") as in_:
        fingerprint = json.load(in_)

    decoded = bytes.fromhex(item).decode('utf-8')
    data_list = decoded.split(" ")

    fingerprint["fingerprints"]["memory"]["hash"] = data_list[2]
    fingerprint["uuid"] = data_list[3]

    return fingerprint


def check_block(template_path: Path, data_list, asset_pt, access_chain_two, addresses_chain_two):
    logging.debug("check_block:")

    if data_list:
        for item in data_list:
            logging.debug(f"item: {item}, type(item): {type(item)}")

            if not isinstance(item, dict):
                fingerprint = get_fingerprint(template_path, item)

                logging.info(f"fingerprint:{json.dumps(fingerprint, indent=4)}")

                res_tx_id = asset_pt.send_with_data(addresses_chain_two[1], access_chain_two, item)
                logging.debug(f"Tx ID: {res_tx_id}")


def do_run(template_path: Path,
           chain_one_name, chain_one_port, chain_one_password,
           chain_two_name, chain_two_port, chain_two_password, skip_blockchain_two):
    logging.info("Connecting with the chain one")

    pt_chain_one = connect.BlockchainConnect(chain_one_port, chain_one_name, chain_one_password)
    access_chain_one = pt_chain_one.start()
    asset_pt = asset.AssetCreate()
    handler = blockhandler.BlockHandler(access_chain_one)

    if not skip_blockchain_two:
        logging.info("Starting with the chain two")
        pt_chain_two = connect.BlockchainConnect(chain_two_port, chain_two_name, chain_two_password)
        access_chain_two = pt_chain_two.start()
        addresses_chain_two = []
        addresses_chain_two.extend(access_chain_two.getaddresses())
        if 1 <= len(addresses_chain_two) <= 2:
            addresses_chain_two.extend(access_chain_two.getnewaddress())

        access_chain_two.grant(addresses_chain_two[1], "receive,send")

        asset_pt.set_asset_params([settings.ASSET_NAME, True, addresses_chain_two[0], settings.QUANTITY])

        asset_tx_id_chain_two = asset_pt.asset_creation(access_chain_two)

    height_store = HeightStore(Path("height.dat"))

    height = 0
    next_height = height_store.load()

    logging.debug(f"next_height: {next_height}")

    while True:

        try:
            height = handler.retrieve_block_height(access_chain_one)
            logging.debug(f"Height: {height}, Next height: {next_height}")
            if height >= next_height:

                logging.debug(f"range({next_height}, ({height + 1}))")

                for i in range(next_height, (height + 1)):
                    block = handler.get_block(access_chain_one, i)
                    data = handler.explore_block(block)

                    logging.debug(f"    data={data}")

                    if not skip_blockchain_two:
                        check_block(template_path, data, asset_pt, access_chain_two, addresses_chain_two)

                next_height = i + 1

            time.sleep(2)
        finally:
            height_store.save(height)


def main():
    parser = argparse.ArgumentParser("Run a relay.")

    parser.add_argument("--chain-one-name", help="The name of the first Blockchain", required=True)
    parser.add_argument("--chain-one-port", help="Port used by the first Blockchain", type=int, required=True)
    parser.add_argument("--chain-one-password", help="Password used by the first Blockchain")
    parser.add_argument("--chain-two-name", help="The name of the second Blockchain", default=None)
    parser.add_argument("--chain-two-port", help="Port used by the second Blockchain", type=int, default=None)
    parser.add_argument("--chain-two-password", help="Password used by the first Blockchain")
    parser.add_argument("--template-path", help="template path", required=True)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("--debug", help="set debug print", action="store_true", default=False)
    parser.add_argument("-dme", "--disable-multichain-cli-errors", action="store_true", default=False)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args.disable_multichaincli_errors:
        logger = logging.getLogger("multichaincli.client")
        logger.setLevel(logging.FATAL)

    if args.chain_two_name is None and args.chain_two_port is None:
        skip_blockchain_two = True
    elif args.chain_two_name is not None and args.chain_two_port is not None:
        skip_blockchain_two = False
    else:
        parser.error("chain two password/port must be both either set or not set")

    do_run(
        Path(args.template_path),
        args.chain_one_name, args.chain_one_port, args.chain_one_password,
        args.chain_two_name, args.chain_two_port, args.chain_two_password, skip_blockchain_two
    )


if __name__ == '__main__':
    main()
