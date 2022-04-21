import os

from multichaincli import Multichain


class BlockchainConnect(object):

    def __init__(self, port, chain_name, password):
        self.id = "multichainrpc"
        self.name = chain_name
        self.host = "127.0.0.1"
        self.port = port
        self.http = "http://"
        self.id_path = os.environ['HOME'] + "/.multichain/" + chain_name + "/multichain.conf"
        self.password = password

    def start(self):

        chain_pass = self.password

        if chain_pass is None:
            # Load chain pass from ID_PATH
            with open(self.id_path, "r") as fp:
                for i, line in enumerate(fp):
                    tokens = line.strip().split("=")
                    if tokens[0] == "rpcpassword":
                        chain_pass = tokens[1]
                        break

        return Multichain(self.id, chain_pass, self.host, self.port, self.name)
