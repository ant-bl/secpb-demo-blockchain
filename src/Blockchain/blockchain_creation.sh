#!/usr/bin/env bash

green=`tput setaf 2`
reset=`tput sgr0`

if [ $# -eq 1 ]
then
	
	echo "\n \n $green Stopping Blockchain if already existing... $reset"
	multichain-cli $1 stop
	sleep 3
	echo "\n \n$green Creating new Blockchain...$reset"
	multichain-util create $1 
	echo "\n\n $green Starting the Blockchain...$reset"
	multichaind  $1 -daemon
	
	sleep 3
	echo "\n\n $green Getting blockchain info... $reset"
	multichain-cli $1 getinfo
	sleep 2
	
	
	gnome-terminal -- sh -c "multichain-cli $1 getaddresses; bash"
	
else
	echo "ERROR: Please provide a Blockchain name as script argument! \n"
fi
