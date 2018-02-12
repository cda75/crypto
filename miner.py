# -*- coding: utf-8 -*-

import os
from datetime import datetime
from time import sleep
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 
import threading


class Miner(object):
	def __init__(self, coin='ZEC', log=False):
		self.__set_parameters(coin)
		self.log = log
		self.__equihash_bin = 'dtsm'	
		#thread = threading.Thread(target=self.run, args=())
		#thread.daemon = True                         
		#thread.start()

	def __set_parameters(self, coin):
		self.__coin = coin
		cfg = SafeConfigParser()
		cfg.read(COINS)
		self.__algo = cfg.get(coin, 'ALGO')
		self.__port = cfg.get(coin, 'PORT')
		self.__pool = cfg.get(coin, 'POOL')
		self.__user = cfg.get(coin, 'USER')
		self.__addr = cfg.get(coin, 'ADDR')
		self.__worker = cfg.get(coin, 'WORKER')
		self.__password = cfg.get(coin, 'PASSWORD')
		cfg.read(CONFIG)
		self.__bin = cfg.get('ALGO', self.__algo)
		self.__pid = os.path.basename(self.__bin)

	def set_coin(self, coin):
		self.__coin = coin

	def get_coin(self):
		return self.__coin

	def get_algo(self):
		return self.__algo

	def get_pid(self):
		return self.__pid

	def set_equihash_bin(self, prog_bin):
		self.__equihash_bin = prog_bin

	def __logging(self, info):
		time = "[%s] " %datetime.strftime(datetime.now(), "%d/%m %H:%M:%S")
		print time+info
		if self.log:
			with open(LOG, 'a') as f:
				f.write(time+info+'\n')

	def __write_pid(self):
		
		
	def run(self):	
		if self.__algo == 'equihash':
			if self.__equihash_bin == 'ewbf':
				cmdStr = "%s --server %s --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(miner_bin, pool, port, user, worker)
			else:
				cmdStr = "%s --server %s --port %s --user %s.%s --telemetry=0.0.0.0:42000" %(miner_bin, pool, port, user, worker)
		elif self.__algo == 'ethash':
			cmdStr = "%s -di 023 -epool %s:%s -ewal %s.%s " %(self.__bin, self.__pool, self.__port, self.__user, self.__worker)
		else:
			cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(self.__bin, self.__algo, self.__pool, self.__port, self.__user, self.__worker)
		try:
			Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
			with open(PID, 'w') as f:
				f.write(self.__pid)
			with open(COIN, 'w') as f:
				f.write(self.__coin)
			self.__logging("[+] Successfully started %s mining\n" %self.__coin)
		except:
			self.__logging("[-] ERROR started %s mining\nExit\n" %self.__coin)
			exit()

	
	def start(self):
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                         
		thread.start()

	def stop(self):
		cmdStr = "taskkill /f /im %s" %(self.__pid)
		try:	
			os.system(cmdStr)
		except:
			return False



	def restart(self):
		pass
	def check(self):
		pass

