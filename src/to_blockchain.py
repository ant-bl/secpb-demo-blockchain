#!/usr/bin/env python3


import hashlib
from bitcoinrpc.authproxy import JSONRPCException
import asset
import blockhandler
import connectionNew as connect
import logging
import socket



class Send_to_blockchain ():

    def __init__(self, name, port,data):

        self.Adresses=[]
        self.ASSET_NAME="SECPB"
        self.QUANTITY=1000000
        self.blockchainPort=port
        self.chainName=name
        self.data=data
        self.connect()


    def connect(self):
        asset_pt=asset.AssetCreate()
        print("Starting with the chain One:  \n")
        pt_chainOne=connect.BlockchainConnect(self.blockchainPort,self.chainName)
        access_chainOne=pt_chainOne.start()
        self.Adresses.extend(access_chainOne.getaddresses())
        if len(self.Adresses)>= 1 and len(self.Adresses)<= 2:
                self.Adresses.extend(access_chainOne.getnewaddress())
                print("First address -->",self.Adresses[1])

            
        access_chainOne.grant(self.Adresses[1],"receive,send") 
        asset_pt.set_asset_params([self.ASSET_NAME,True,self.Adresses[0],self.QUANTITY])

        try :
                assetTXID=asset_pt.asset_creation(access_chainOne)
        except :
                print ("Asset existing !")

        self.send(asset_pt,access_chainOne)


    def send(self, asset, access):
        tmp="vm_dst"+""+self.chainName+self.data["fingerprint"]["fingerprints"]["memory"]["hash"]+" "+self.data["fingerprint"]["uuid"]

        data_hex=tmp.encode("utf-8").hex()
        print("Data hex is", data_hex)
        resTXID=asset.sendWithData(self.Adresses[1],access,data_hex)
        print("Tx ID",resTXID)

        #self.do_run(resTXID, "127.0.0.1:9008")



    
