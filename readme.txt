
************************************* SECPB Blockchain intercommunication Project***************************

The SECPB repo is composed by:



-- script repo
	|-- blockchain.sh : This script allow Multichain installation, Blcockhain creation and Blcockhain connection.

-- data repo
	|--fingerprin.json : This file contains the vm hash  to be sent

-- lib
	|-- asset.py : This file contains functions for assets creation and management in the blockchain
	|-- blockchainhandler.py: This file contains function for the management of transactions and blocks in the Blockchain
	|-- connection.py: This file contains function for the connection establishment between an app and the Blockchain

--fake_dst_vm.py : Used to start an HTTP server in order to receive  transaction ID
--fake_dst_vm_2.py : Used to start an HTTP server in order to receive  transaction ID
--send_data.py : Used to send a hash in a blockchain
--receive_data: Used for getting a hash from a Blcockhain
--relayer: Used to retrieve an hash from a blockchain and send to another.



         Node 1								       Node 2						      Node 3
  |***********************|         TXID 1      |********************|		TXID2		|*******************|				
  |			  			  |-------------------> |tx_rec_chain_one.py------------------->|tx_receiver_chain  |
  |fake_Blcokchain_src.py |						|********************|					|*******************|
  |			              |						|relayer.py          |					|received_data.py   |
  |***********************|						|********************|					|*******************|
		|								|   |							|
		|								|   |							|
		|								|   |							|
		|	hash		|---------------|	hash		|   |		hash	|-------------|		hash	|
		|---------------------->| Blockchain 1  |------------->---------|   |----------->-------|Blockchain 2 |------->---------|
					|---------------|						|-------------|


					
