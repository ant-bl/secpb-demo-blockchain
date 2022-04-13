import json
import hashlib
import binascii

class AssetCreate():
    """Class for asset creation"""

    def __init__(self):
        self.name = ""
        self.open = True
        self.address = ""
        self.qty =1
        self.minAmount = 0.01


    def asset_creation(self,access):
        asset_params={"name":self.name,"open":self.open}
        try:
            transactionID=access.issue(self.address,asset_params,self.qty,self.minAmount)
            print("Transaction Id", transactionID)
            return transactionID

        except :
            print("Asset already exist !")

    def set_asset_params(self, target):
        self.name = target[0]
        self.open = target[1]
        self.address = target[2]
        self.qty = target[3]
        self.minAmount = 0.01

    
    def sendWithData(self,address,access,data):

        print("Data hex is: ", data)
        transactionID=access.sendwithdata(address,{self.name : self.qty},data)

        return transactionID
