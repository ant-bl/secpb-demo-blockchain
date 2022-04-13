#!/usr/bin/env python3


import argparse
import time

import asset
import blockhandler
import connectionNew as connect

ASSET_NAME = "SECPB"
QUANTITY = 1000000


def check_block(data_list, asset_pt, access_chain_two, adresses_chain_two):
    if data_list:
        for item in data_list:
            if type(item) != 'dict':
                print("Data value: ", item)
                resTXID = asset_pt.sendWithData(adresses_chain_two[1], access_chain_two, item)
                print("Tx ID: ", resTXID)


def retrieve_saved_block_height():
    try:
        with open('height.dat', 'r') as file:
            height = file.read()
            print("Lines", height)

            if height:
                return height

            file.write("0")
            return 0

    except FileNotFoundError:
        with open('height.dat', 'a+'):
            pass
        retrieve_saved_block_height()


def save_height(height):
    try:
        with open('height.dat', 'w+') as file:
            file.write(str(height))
    except FileNotFoundError:
        with open('height.dat', 'a+') as file:
            file.write(height)


def main():
    parser = argparse.ArgumentParser("Run a relayer.")

    parser.add_argument("--chain-one-name", help="The name of the first Blockchain", required=True)
    parser.add_argument("--chain-one-port", help="Port used by the first Blockchain", type=int, required=True)
    parser.add_argument("--chain-one-password", help="Password used by the first Blockchain")
    parser.add_argument("--chain-two-name", help="The name of the second Blockchain", required=True)
    parser.add_argument("--chain-two-port", help="Port used by the second Blockchain", type=int, required=True)
    parser.add_argument("--chain-two-password", help="Password used by the first Blockchain")

    args = parser.parse_args()

    print("Starting with the chain One:  \n")
    pt_chain_one = connect.BlockchainConnect(args.chain_one_port, args.chain_one_name, args.chain_one_password)
    access_chain_one = pt_chain_one.start()
    asset_pt = asset.AssetCreate()
    handler = blockhandler.BlockHandler(access_chain_one)

    print("Starting with the chain Two:  \n")
    pt_chain_two = connect.BlockchainConnect(args.chain_two_port, args.chain_two_name, args.chain_two_password)
    access_chain_two = pt_chain_two.start()
    adresses_chain_two = []
    adresses_chain_two.extend(access_chain_two.getaddresses())
    if len(adresses_chain_two) >= 1 and len(adresses_chain_two) <= 2:
        adresses_chain_two.extend(access_chain_two.getnewaddress())

    access_chain_two.grant(adresses_chain_two[1], "receive,send")

    asset_pt.set_asset_params([ASSET_NAME, True, adresses_chain_two[0], QUANTITY])

    asset_txid_chain_two = asset_pt.asset_creation(access_chain_two)
    last_height = int(retrieve_saved_block_height())
    height = 0

    while True:

        try:
            height = handler.retrieveBlockheight(access_chain_one)
            # print(" Block  height retrieved !")
            print("Height: ", height, "Last height: ", last_height)
            if height > last_height:
                for i in range(last_height, (height + 1)):
                    block = handler.getBlock(access_chain_one, i)
                    data = handler.explore_block(block)

                    check_block(data, asset_pt, access_chain_two, adresses_chain_two)

                last_height = height

            time.sleep(2)

        finally:
            save_height(height)


if __name__ == '__main__':
    main()
