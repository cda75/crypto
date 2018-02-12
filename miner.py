# -*- coding: utf-8 -*-

import os
from datetime import datetime
from time import sleep
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 
import threading



WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(WORK_DIR, 'config.conf')
COINS = os.path.join(WORK_DIR, 'coins.conf')
BENCHMARK = os.path.join(WORK_DIR, 'benchmark.conf')
NICEHASH = os.path.join(WORK_DIR, 'nicehash.conf')
LOG = os.path.join(WORK_DIR, 'mining.log')
PID = os.path.join(WORK_DIR, 'PID')
COIN = os.path.join(WORK_DIR, 'COIN')


class Miner(object):
	def __init__(self, coin='ZEC', log=False):
		self.__set_parameters(coin)
		self.log = log
		self.__equihash_bin = 'dtsm'

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
		self.__pid = [os.path.basename(self.__bin)]

	def set_coin(self, coin):
		self.__set_parameters(coin)

	def set_gpu(self, gpu):
		self.__gpu = gpu

	def get_coin(self):
		return self.__coin

	def get_algo(self):
		return self.__algo

	def get_pid(self):
		return self.__pid

	def get_pool(self):
		return self.__pool

	def get_bin(self):
		return self.__bin

	def get_addr(self):
		return self.__addr

	def set_equihash_bin(self, prog_bin):
		self.__equihash_bin = prog_bin
		if self.__algo == 'equihash':
			cfg = SafeConfigParser()
			cfg.read(CONFIG)
			self.__bin = cfg.get('ALGO', prog_bin.lower())
			self.__pid = os.path.basename(self.__bin)

	def __logging(self, info):
		time = "[%s] " %datetime.strftime(datetime.now(), "%d/%m %H:%M:%S")
		print time+info
		if self.log:
			with open(LOG, 'a') as f:
				f.write(time+info+'\n')	
		
	def start(self):
		cmdStr = []
		if self.__algo == 'equihash':
			if self.__equihash_bin == 'ewbf':
				cmdStr.append("%s --server %s --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			else:
				cmdStr.append("%s --server %s --port %s --user %s.%s --telemetry=0.0.0.0:42000" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
		elif self.__algo == 'ethash':
			cmdStr.append("%s -di 023 -epool %s:%s -ewal %s.%s " %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			self.__set_parameters('ZEC')
			if self.__equihash_bin == 'ewbf':
				cmdStr.append("%s --server %s --cuda_devices 1 --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			else:
				cmdStr.append("%s --server %s --dev 1 --port %s --user %s.%s --telemetry=0.0.0.0:42000" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			self.__coin = "ETH ZEC"
			self.__pid.append('ZEC')
		else:
			cmdStr.append("%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(self.__bin, self.__algo, self.__pool, self.__port, self.__user, self.__worker))
		try:
			for cmd in cmdStr:
				Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
			self.__logging("[+] Successfully started %s mining\n" %self.__coin)
		except:
			self.__logging("[-] ERROR started %s mining\nExit\n" %self.__coin)
			exit()

	def stop(self):
		for pid in self.__pid:
			cmdStr = "taskkill /f /im %s" %(pid)
			try:	
				os.system(cmdStr)
			except:
				self.__logging("[-] Error stopping process\n" %pid)

	def restart(self):
		pass
	def check(self):
		pass

