#!/usr/bin/env python3


import asset
import blockhandler
import connection as connect
import os
import time
import logging



Adresses_chainOne=[]
Adresses_chainTwo=[]
chainOne_name="secpbChain"
chainOne_port="9234"
chainTwo_name="secpb-chain"
chainTwo_port="6308"
ASSET_NAME="SECPB"
QUANTITY=1000000
HOME_NAME=os.environ['HOME']
DEST_PATH="127.0.0.1:9895"
lastHeight = 0
Height=0





def check_block (data_list):
    if data_list :
            for item in data_list:
                if type(item) != 'dict':
                    print("Data value: ",item)
                    resTXID=asset_pt.sendWithData(Adresses_chainTwo[1],access_chainTwo,item)
                    print("Tx ID: ",resTXID)

def retreive_saved_block_height():
    try:

        file = open('height.dat','r')
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
        open('height.dat','a+').close()
        retreive_saved_block_height()


def save_height(height):
    try:

        file = open('height.dat','w+')
        file.write(str(height))
        file.close()


    except FileNotFoundError:
        file = open('height.dat','a+')
        file.write(height)
        file.close()



if __name__ == '__main__':



        print("Starting with the chain One:  \n")
        pt_chainOne=connect.BlockchainConnect(chainOne_port,chainOne_name)
        access_chainOne=pt_chainOne.start()
        asset_pt=asset.AssetCreate()
        handler=blockhandler.BlockHandler(access_chainOne)

        print("Starting with the chain Two:  \n")
        pt_chainTwo=connect.BlockchainConnect(chainTwo_port,chainTwo_name)
        access_chainTwo=pt_chainTwo.start()
        Adresses_chainTwo.extend(access_chainTwo.getaddresses())
        if len(Adresses_chainTwo)>= 1 and len(Adresses_chainTwo)<= 2:
            Adresses_chainTwo.extend(access_chainTwo.getnewaddress())
        
        access_chainTwo.grant(Adresses_chainTwo[1],"receive,send")   

        asset_pt.set_asset_params([ASSET_NAME,True,Adresses_chainTwo[0],QUANTITY])


        try :
            assetTXID_chainTwo=asset_pt.asset_creation(access_chainTwo)
        except JSONRPCException as e:
            print ("Asset existing")

        lastHeight=int(retreive_saved_block_height())

        while True:

            try:
                Height=handler.retrieveBlockheight(access_chainOne)
                #print(" Block  height retrieved !")
                print("Height: ", Height, "Last height: ", lastHeight)
                if Height > lastHeight:
                    for i in range(lastHeight,(Height+1)):
                        block=handler.getBlock(access_chainOne,i)
                        data=handler.explore_block(block)

                        check_block (data)

                    lastHeight=Height
                
                time.sleep(15)

            finally :
                save_height(Height)

        
            

        

       
        


        #do_run(resTXID, DEST_PATH)

        
    

	
