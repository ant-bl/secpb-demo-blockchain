#!/usr/bin/env python3

import argparse
import logging
import time
from pathlib import Path

import asset
import blockhandler
import connection as connect
import settings
from height_store import HeightStore


def check_block(data_list, asset_pt, access_chain_two, addresses_chain_two):
    logging.info("check_block:")

    if data_list:
        for item in data_list:
            logging.info(f"item: {item}, type(item): {type(item)}")

            if type(item) != 'dict':
                res_tx_id = asset_pt.send_with_data(addresses_chain_two[1], access_chain_two, item)
                logging.info(f"Tx ID: {res_tx_id}")


def do_run(chain_one_name, chain_one_port, chain_one_password,
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

    logging.info(f"next_height: {next_height}")

    while True:

        try:
            height = handler.retrieve_block_height(access_chain_one)
            logging.info(f"Height: {height}, Next height: {next_height}")
            if height >= next_height:

                logging.info(f"range({next_height}, ({height + 1}))")

                for i in range(next_height, (height + 1)):
                    block = handler.get_block(access_chain_one, i)
                    data = handler.explore_block(block)

                    logging.info(f"    data={data}")

                    if not skip_blockchain_two:
                        check_block(data, asset_pt, access_chain_two, addresses_chain_two)

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
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args.chain_two_name is None and args.chain_two_port is None:
        skip_blockchain_two = True
    elif args.chain_two_name is not None and args.chain_two_port is not None:
        skip_blockchain_two = False
    else:
        parser.error("chain two password/port must be both either set or not set")

    do_run(args.chain_one_name, args.chain_one_port, args.chain_one_password,
           args.chain_two_name, args.chain_two_port, args.chain_two_password, skip_blockchain_two)


if __name__ == '__main__':
    main()
