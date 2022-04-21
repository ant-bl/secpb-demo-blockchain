class BlockHandler:

    def __init__(self, chain_pt):
        self.chain = chain_pt
        self.height = 0

    def retrieve_block_height(self, pt):
        block_info = pt.getblockchaininfo()
        self.height = block_info["blocks"]
        return self.height

    def get_block(self, pt, height):
        return pt.getblock(str(height))

    def get_block_hash(self, pt, height):
        return pt.getblockhash(str(height))

    def get_transaction_out(self, pt, tx_id, v_out):
        return pt.gettxout(tx_id, str(v_out))

    def get_transaction_out_data(self, pt, tx_id, v_out):
        return pt.gettxoutdata(tx_id, v_out)

    def get_chain_transaction_out_data(self, tx_id, v_out):
        return self.chain.gettxoutdata(tx_id, v_out)

    def explore_block(self, block):
        out = []
        tx_list = block['tx']
        for item in tx_list:
            try:
                tx_data = self.get_chain_transaction_out_data(item, 1)
                if type(tx_data) != 'dict':
                    out.append(tx_data)
            except Exception:
                pass

        return out
