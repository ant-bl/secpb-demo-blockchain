# Readme #

## TIPS ##

Get info on blockchain :
```
multichain-cli secpbChain
getinfo
getaddresses
```

Setup venv :
```
pip install multichaincli
```

Delete a blockchain :
```
rm -rf .multichain/secpbChain/
```

401 error : check password

Inspect a transaction in a blockchain :

```
multichain-cli secpb-chain
```

```
>>> secpb-chain: subscribe SECPB
{"method":"subscribe","params":["SECPB"],"id":"91571222-1649774726","chain_name":"secpb-chain"}

>>> secpb-chain: getassettransaction SECPB d695f7dfa585dedebeaf34e1f537b556c471448bcc4c0edf763ea1d0e8d0f484

{"method":"getassettransaction","params":["SECPB","d695f7dfa585dedebeaf34e1f537b556c471448bcc4c0edf763ea1d0e8d0f484"],"id":"84892784-1649774728","chain_name":"secpb-chain"}

{
    "addresses" : {
        "1CVpx1k7mEAtYaMGM3Fh6HYriQ6GTWsWZPLPsA" : 0
    },
    "items" : [
    ],
    "data" : [
        "766d5f6473747365637062436861696e32623533323662656433386266386233343466346661646461616138306531663634323862383434623338343235316534333163613133353332343831323362206f5558626441457443537479677966647a79745259666479"
    ],
    "confirmations" : 11,
    "blockhash" : "00db1a29ff691e79b51d04b3cd647a749e00975e2fe008afc8a93d904a4e7efe",
    "blockheight" : 125,
    "blockindex" : 1,
    "blocktime" : 1649774551,
    "txid" : "d695f7dfa585dedebeaf34e1f537b556c471448bcc4c0edf763ea1d0e8d0f484",
    "valid" : true,
    "time" : 1649774551,
    "timereceived" : 1649774679
}
secpb-chain:                                                                            
```

## Schema ##

```
+------------------------+
| fake_src_blockchain.py |
+------------------------+
| secpb_vm_migration_1   |
+------------------------+
|   127.0.0.1:7452       |
|   192.168.1.1:7453     |-----+
+------------------------+     |
                               |
+------------------------+     |
| relayer.py             |     | secpbChain
+------------------------+     |
| secpb_vm_migration_nfs |     |
+------------------------+     |
|   127.0.0.1:7452       |     |
|   192.168.1.3:7453     |-----+
|   127.0.0.1:6830       |
|   192.168.1.3:6831     |-----+
+------------------------+     |
                               |
+------------------------+     |
| fake_dst_blockchain.py |     | secpb-chain
+------------------------+     |
| secpb_vm_migration_2   |     |
+------------------------+     |
|   127.0.0.1:6830       |     |
|   192.168.1.2:6831     |-----+
+------------------------+
```

## secpb_vm_migration_1 ##

Run blockchain :
```
./Blockchain/blockchain.sh -cc secpbChain
```

Run source code :
```
python3 fake_src_blockchain.py --path "/home/user/Secpb/fingerprint.json" \
        --chain-name secpbChain \
        --chain-port 7452
```

Password is coming from `~/.multichain/secpbChain/multichain.conf`

## secpb_vm_migration_nfs ##

Connect to first blockchain :
```
./Blockchain/blockchain.sh -cc secpbChain 192.168.1.1 7453
```

Donner l'accès sur `secpb_vm_migration_1` au serveur `secpb_vm_migration_nfs`. Sur `server_1` : 
```
multichain-cli secpbChain grant 1WZEaC5myAXGsaFzaKpxwfm9r7yWV5p8qDp83P connect,send,receive,issue,activate
```

Run second blockchain :
```
./Blockchain/blockchain.sh -cc secpb-chain
```

Run source code :
```
python3 ./relayer.py --chain-one-name secpbChain --chain-one-port 7452 --chain-two-name secpb-chain --chain-two-port 6830
```

## secpb_vm_migration_2 ##

Connect to second blockchain :

```
./Blockchain/blockchain.sh -cc secpb-chain 192.168.1.3 6831
```

Donner l'accès sur `secpb_vm_migration_nfs` au serveur `secpb_vm_migration_2`. Sur `secpb_vm_migration_nfs` :

```
multichain-cli secpb-chain grant 1CP1KTMtKjiUyAZoGfcK6UwrAus6BPSkyetfuH connect,send,receive,activate,issue
```

Run source code :
```
./fake_dst_blockchain.py --socket-path /tmp/test.json --chain-name secpb-chain --chain-port 6830 --path ./fingerprint.json
``` 

## Création manuelle avec timer ##

Création de la chaine : 
```
multichain-util create secpbChain
multichain-util create secpb-chain 
```

Update blockchain timer in `/home/user/.multichain/secpb-chain/params.dat` :
```
vim /home/user/.multichain/secpbChain/params.dat
vim /home/user/.multichain/secpb-chain/params.dat
```

```
cat /home/user/.multichain/secpb-chain/params.dat | grep target-block-time
target-block-time = 2                  # Target time between blocks (transaction confirmation delay), seconds. (2 - 86400)
```

Update all sleep in code. TODO

Run as daemon :
```
multichaind secpbChain -daemon
multichaind secpb-chain -daemon
```