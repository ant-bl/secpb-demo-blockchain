#!/usr/bin/env python3


import argparse
import json
import logging
import socket
import os
import asset
import blockhandler
import connection as connect
import time

HOME_NAME=os.environ['HOME']
PATH=HOME_NAME +"/Downloads/Secpb/fingerprint.json"
http_address="127.0.0.1"
http_port="9997"

socket_path="/tmp/fake_dst.unix"
lastHeight = 0
Height=0


def do_write_fingerprint_unix( socket_path: str, js: str):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(socket_path)
        client.send(json.dumps(js, ensure_ascii=True).encode("utf8"))

def do_run(path: str,  raw_data: str, socket_path: str):
    
    with open(path, "r") as in_:
        fingerprint = json.load(in_)
    
    fingerprint["fingerprints"]["memory"]["hash"]=data_list[0]
    fingerprint["uuid"]=data_list[1]

    do_write_fingerprint_unix( socket_path, fingerprint)
    #print("socket_path: ",socket_path)


def main():
    parser = argparse.ArgumentParser("Run a server that accepts fingerprint through unix socket and forward it to " +
                                     "an HTPP server through a POST connection.")

    parser.add_argument("--path", help="path that will used to read the fingerprint. If the paths starts by unix: " +
                                       "the fingerprint will be read through a socket unix")
    parser.add_argument("--chainName", help="The name of Blockchain", required=True)
    parser.add_argument("--chainPort", help="Port used by the Blockchain", required=True)
    parser.add_argument("--socket_path", help="socket path to reach vm dest", required=True)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true", default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    return args

def retreive_saved_block_height():
    try:

        file = open('height_dst.dat','r+')
        height=file.read()
        print("LInes",height)
        
        if height :
            file.close()
            return height
            

        else:
            
            file.write("0")
            file.close()
            return 0

    except FileNotFoundError:
        open('height_dst.dat','a+')
        retreive_saved_block_height()


def save_height(height):
    try:

        file = open('height_dst.dat','w+')
        file.write(str(height))
        file.close()


    except FileNotFoundError:
        file = open('height_dst.dat','a+')
        file.write(height)
        file.close()

def send_data(data_to_send,socket_path):
    for item in data_to_send:
        try:
            decoded=bytes.fromhex(item).decode('utf-8')
            data_list= decoded.split(" ")
            print("Received data", data_list)
            if data_list[0]== "vm_dst":
                do_run(PATH, socket_path )
        except UnicodeDecodeError :
            pass
        


if __name__ == '__main__':

    args=main()
    print("Starting with the chain One:  \n")
    pt_chainOne=connect.BlockchainConnect(args.chainPort,args.chainName)
    access_chainOne=pt_chainOne.start()
    asset_pt=asset.AssetCreate()
    handler=blockhandler.BlockHandler(access_chainOne)

    lastHeight=int(retreive_saved_block_height())
    print("Last height value",lastHeight)
    while True:

        try:
            Height=handler.retrieveBlockheight(access_chainOne)
            #print(" Block  height retrieved !")
            print("Height: ", Height, "Last height: ", lastHeight)
            if Height > lastHeight:
                for i in range(lastHeight,(Height+1)):
                    block=handler.getBlock(access_chainOne,i)
                    data=handler.explore_block(block)
                    send_data(data,args.socket_path)

                lastHeight=Height
            time.sleep(15)

        finally :
            save_height(Height)

    

