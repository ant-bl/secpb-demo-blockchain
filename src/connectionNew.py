from multichaincli import Multichain
import json
import os


class BlockchainConnect(object):


    
    def __init__(self, port,chainName):
        self.id="multichainrpc"
        self.name=chainName
        self.host="127.0.0.1"
        self.port=port
        self.http="http://"
        self.id_path = os.environ['HOME']+"/.multichain/"+chainName+"/multichain.conf"
        

    def start(self):
    
    	#Load chain pass from ID_PATH
        fp = open(self.id_path, "r")
        for i,lines in enumerate(fp):
            if i==1:
                chain_pass= lines.split("=")

        fp.close()
        chainpass=chain_pass[1]
        
        #arg=self.http+self.ID+":"+chainpass[0:44]+"@"+self.Ip+":"+self.Port
        #mychain=Multichain(self.id, chainpass,self.host,self.port,self.name)
        #print("Infos: ",mychain.getinfo())
        return Multichain(self.id, chainpass[0:44],self.host,self.port,self.name)

