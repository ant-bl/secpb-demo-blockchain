#!/usr/bin/env python3

import sys
import os





while True :
	chainame=input('Please provide the Blockchain name: ')
	if chainame:
		try:
		
			os.system('multichain-util create {}'.format(chainame))
			
		
		except e :
			print("ERROR: Blockchain existing! provide an other name \n")

	else :
		print("ERROR: Please provide a Blockchain name ! \n")
