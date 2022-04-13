# !/bin/bash

green=`tput setaf 2`
reset=`tput sgr0`
ADD="$"


print_infos (){
	echo :'
	
	ERROR: Please provide the right options! \n
	-c  BlockchainName		Create a Blockchain. This option must be followed by the of the Blockchain that we want to create. This option start automatically the created chain. Start also already existing Blockchain	\n
	-cc BlockchainName IP port	Connect to an existing Blockchain \n
	-i  Install multichain		Install multichain software \n
	-s  BlockchainName		Start own existing Blockchain
	
	Example: \n
	./Blockchain -i -c testchain  	--Install multichain and create new Blockchain \n
	./Blockchain -i -cc testchain 127.0.0.1 8989  	--Install multichain and create and connect to an already created Blockchain \n
	./Blockchain -cc testchain 127.0.0.1 8989  	--connect to an already created Blockchain \n
	'
}

print_connection_infos (){
	echo :'
	
	You are not connected yet ! \n
	You must to provide your account address to the Blockchain admin. Your adresse is provided above! \n
	
	The admin must to execute:
	
		multichain-cli $2 grant xxxxxxxxxxxxxxxxx connect,send,receive,activate,issue
	
	Then, try to reconnect:
		multichaind	BlockchainName@IP_adresse:Port
	'
}

print_admin_infos (){
	echo :'
	
	The Blockchain i created and your are the admin ! \n 
	Others can be connect to you Blokchain, by provinding account address. You will then provide the appropriate rights with the command described below\n
	
	
		multichain-cli blockchainName grant xxxxxxxxxxxxxxxxx connect,send,receive,activate,issue \n
	
	
	'
}

if [ $# -eq 0 ]
then
	print_infos
else

	while : ;
	do

		case "$1" in -c)

			echo "\n \n $green Stopping Blockchain if already existing... $reset"
			multichain-cli $2 stop
			sleep 3
			echo "\n \n$green Creating new Blockchain...$reset"
			multichain-util create $2
			echo "\n\n $green Starting the Blockchain...$reset"
			multichaind  $2 -daemon
			
			sleep 3
			print_admin_infos

			gnome-terminal -- sh -c "multichain-cli $2 getinfo; multichain-cli $2 getaddresses; bash"
			shift 2
			;;
		-i )
			echo "Starting multichain install: $1"
			cd /tmp
			wget https://www.multichain.com/download/multichain-2.2.tar.gz
			tar -xvzf multichain-2.2.tar.gz
			cd multichain-2.2
			mv multichaind multichain-cli multichain-util /usr/local/bin
			shift 1

			;;
		-cc )
			echo "\n \n $green Stopping Blockchain if already running... $reset"
			multichain-cli $2 stop
			sleep 3
			echo "Starting connection with  $2 ..."
			echo "multichain-cli $2@$3:$4"
			multichaind $2@$3:$4
			sleep 4
			print_connection_infos
			#gnome-terminal -- sh -c "multichain-cli $2 getaddresses; bash"

			shift 3
			;;
		-s )
			echo "\n \n $green Stopping Blockchain if already running... $reset"
			multichain-cli $2 stop
			sleep 3
			echo "$green  Starting $2 ... $reset"
			
			multichaind $2 -daemon
			sleep 4
			#gnome-terminal -- sh -c "multichain-cli $2 getaddresses; bash"
			
			#shift 3
			;;
			
		*)
			echo "End of options..."
			break
			;;
		esac	
			

	done

fi


