


class BlockHandler():

   def __init__(self,chain_pt):
       self.chain=chain_pt
       self.height=0

   
   def retrieveBlockheight(self,pt):
       blockinf=pt.getblockchaininfo()
       self.height=blockinf["blocks"]
       return self.height

   def getBlock(self,pt,height):
      return pt.getblock(str(height))
      
   def getblockHASH(self,pt, height):
      return pt.getblockhash(str(height))

   def getTransactionOUT(self,pt, txID, VOUT):
      return pt.gettxout(txID,str(VOUT))

   def getTransactionOutDATA(self,pt, txID, VOUT):
      return pt.gettxoutdata(txID,VOUT)

   def get_transaction_out_DATA(self,txID, VOUT):
      return self.chain.gettxoutdata(txID,VOUT)

   def explore_block(self, block):
      out=[]
      tx_list=block['tx']
      for item in tx_list:
         try:
            tx_data=self.get_transaction_out_DATA(item, 1)
            if type(tx_data) != 'dict':  
               out.append(tx_data)
            
         except :

            pass

      return out

  


