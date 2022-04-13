import json
import os
from multichaincli import Multichain


class BlockchainConnect(object):

    def __init__(self, port, chainName, password):
        self.id = "multichainrpc"
        self.name = chainName
        self.host = "127.0.0.1"
        self.port = port
        self.http = "http://"
        self.id_path = os.environ['HOME'] + "/.multichain/" + chainName + "/multichain.conf"
        self.password = password

    def start(self):

        if self.password is not None:
            chainpass = self.password
        else:
            # Load chain pass from ID_PATH
            with open(self.id_path, "r") as fp:
                for i, line in enumerate(fp):
                    tokens = lines.strip().split("=")
                    if tokens[0] == "rpcpassword":
                        chain_pass = tokens[1]

            chainpass = chain_pass[1]

        return Multichain(self.id, chainpass, self.host, self.port, self.name)
