# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
from ConfigParser import SafeConfigParser 
import threading
from time import sleep
from operator import itemgetter


WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(WORK_DIR, 'config.conf')
COINS = os.path.join(WORK_DIR, 'coins.conf')
LOG = os.path.join(WORK_DIR, 'mining.log')
PID = os.path.join(WORK_DIR, 'PID')
COIN = os.path.join(WORK_DIR, 'COIN')
LOGGING = "NO" # YES/NO



def logging(info):
	time = "[%s] " %datetime.strftime(datetime.now(), "%d/%m %H:%M:%S")
	print time+info
	if LOGGING == "YES":
		with open(LOG, 'a') as f:
			f.write(time+info+'\n')


class Miner(object):
	def __init__(self, coin='ZEC', log=False):
		self.__set_parameters(coin)
		self.log = log
		self.__equihash_bin = 'dtsm'

	def __set_parameters(self, coin):
		self.__coin = coin
		self.__status = 'OFF'
		cfg = SafeConfigParser()
		cfg.read(COINS)
		self.__algo = cfg.get(coin, 'ALGO')
		self.__port = cfg.get(coin, 'PORT')
		self.__pool = cfg.get(coin, 'POOL')
		self.__user = cfg.get(coin, 'USER')
		self.__addr = cfg.get(coin, 'ADDR')
		self.__worker = cfg.get(coin, 'WORKER')
		self.__password = cfg.get(coin, 'PASSWORD')
		self.__coins = cfg.sections()
		cfg.read(CONFIG)
		self.__bin = cfg.get('ALGO', self.__algo)
		self.__pid = []
		self.__cmd = dict()

	def set_coin(self, coin):
		self.__set_parameters(coin)

	def get_coin(self):
		return self.__coin

	def get_coins(self):
		return self.__coins

	def get_algo(self):
		return self.__algo

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
			self.__pid = [os.path.basename(self.__bin)]

	def __logging(self, info):
		time = "[%s] " %datetime.strftime(datetime.now(), "%d/%m %H:%M:%S")
		print time+info
		if self.log:
			with open(LOG, 'a') as f:
				f.write(time+info+'\n')	
	
	def __write_pid(self):
		with open(PID, 'w') as f:
			for pid in self.__pid:
				f.write(pid+'\n')

	def __write_coin(self):
		with open(COIN, 'w') as f:
			f.write(self.__coin)

	def start(self):
		cmdStr = []
		if self.__algo == 'equihash':
			if self.__equihash_bin == 'ewbf':
				cmdStr.append("%s --server %s --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			else:
				cmdStr.append("%s --server %s --port %s --user %s.%s --telemetry=0.0.0.0:42000" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
		elif self.__algo == 'ethash':
			coin = self.__coin
			self.__set_parameters('ZEC')
			if self.__equihash_bin == 'ewbf':
				cmdStr.append("%s --server %s --cuda_devices 1 --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			else:
				cmdStr.append("%s --server %s --dev 1 --port %s --user %s.%s --telemetry=0.0.0.0:42000" %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
			self.__set_parameters(coin)
			cmdStr.append("%s -di 023 -epool %s:%s -ewal %s.%s " %(self.__bin, self.__pool, self.__port, self.__user, self.__worker))
		else:
			cmdStr.append("%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(self.__bin, self.__algo, self.__pool, self.__port, self.__user, self.__worker))
		try:
			for cmd in cmdStr:
				Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
				pid = os.path.basename(cmd.split()[0])
				self.__pid.append(pid)
				self.__cmd[pid] = cmd
				self.__monitor_pid(pid)
			self.__logging("[+] Successfully started %s mining\n" %self.__coin)
			self.__write_coin()
			self.__write_pid()
			self.__status = "ON"
		except:
			self.__logging("[-] ERROR started %s mining\nExit\n" %self.__coin)
			exit()

	def stop(self):
		for pid in self.__pid:
			cmdStr = "taskkill /f /im %s" %(pid)
			try:	
				os.system(cmdStr)
			except:
				self.__logging("[-] Error stoping process\n" %pid)
		self.__pid = []
		self.__cmd = {}
		self.__write_pid()
		self.__status = "OFF"

	def restart(self):
		coin = self.__coin
		self.stop()
		self.__set_parameters(coin)
		self.start()

	def __restart_pid(self, pid):
		cmd = self.__cmd[pid]
		self.__logging("[i] Trying to restart process %s ....." %pid)
		try:
			Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
			self.__logging("[+] Process Successfully restarted")
		except:
			self.__logging("[-] Process failed to start")

	def __pid_started(self, pid):
		if pid not in Popen('tasklist', stdout=PIPE).communicate()[0]:
			return False
		return True

	def __monitor_pid(self, pid):
		def check_pid():
			while True:
				if not self.__pid_started(pid):
					self.__logging("[-] Ooops! Process %s was crashed!!!" %pid)
					self.__restart_pid(pid)
				sleep(60)
		thread = threading.Thread(target=check_pid)   
		thread.daemon = True                     
		thread.start()




def get_best_coin(coins='all'):
	JSON_URL = r"https://whattomine.com/coins.json?utf8=✓&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=0&adapt_q_570=0&adapt_q_580=3&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=1&adapt_10606=true&adapt_q_1070=2&adapt_1070=true&adapt_q_1070Ti=1&adapt_1070Ti=true&adapt_q_1080=03&adapt_q_1080Ti=0&eth=true&factor%5Beth_hr%5D=113.0&factor%5Beth_p%5D=465.0&grof=true&factor%5Bgro_hr%5D=124.0&factor%5Bgro_p%5D=470.0&x11gf=true&factor%5Bx11g_hr%5D=43.4&factor%5Bx11g_p%5D=450.0&cn=true&factor%5Bcn_hr%5D=2320.0&factor%5Bcn_p%5D=360.0&eq=true&factor%5Beq_hr%5D=1600.0&factor%5Beq_p%5D=450.0&lre=true&factor%5Blrev2_hr%5D=132300.0&factor%5Blrev2_p%5D=470.0&ns=true&factor%5Bns_hr%5D=3550.0&factor%5Bns_p%5D=470.0&lbry=true&factor%5Blbry_hr%5D=1020.0&factor%5Blbry_p%5D=450.0&factor%5Bbk2b_hr%5D=5990.0&factor%5Bbk2b_p%5D=440.0&factor%5Bbk14_hr%5D=9100.0&factor%5Bbk14_p%5D=460.0&pas=true&factor%5Bpas_hr%5D=3580.0&factor%5Bpas_p%5D=450.0&skh=true&factor%5Bskh_hr%5D=104.5&factor%5Bskh_p%5D=450.0&factor%5Bl2z_hr%5D=420.0&factor%5Bl2z_p%5D=300.0&factor%5Bcost%5D=0.1&sort=Profit&volume=0&revenue=current&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=abucoins&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=bleutrade&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=Main&commit=Calculate"	
	if coins != 'all':
		MY_COINS = [x.strip() for x in coins.split(',')]
	else:
		cfg = SafeConfigParser()
		cfg.read(COINS)
		MY_COINS = cfg.sections()
	try:
		logging("[i] Checking best coin...")
		req = requests.get(JSON_URL)
		reqResult = req.json()['coins']
		best_dict = {}
		for value in reqResult.values():
			if value['tag'] in MY_COINS:
				best_dict[value['tag']] = value['profitability']
		rez = sorted(best_dict.items(), key=itemgetter(1), reverse=True)
		best_coin = rez[0][0]
		logging("[i] Current best coin is %s" %best_coin)
		return best_coin
	except:
		logging("[-] Error getting data from WhatToMine....Mining default coin")
		return 'ZEC'


def coin_mining(coins='all', check_time=0.5, run_time=10000):
	m = Miner()
	if (coins == 'all') or (',' in coins):
		best_coin = get_best_coin(coins=coins)
		m.set_coin(best_coin)
		m.start()
		while True:
			sleep(check_time*3600)
			best_coin = get_best_coin(coins=coins)
			if best_coin != m.get_coin():
				m.stop()
				m.set_coin(best_coin)
				m.start()
	else:
		m.set_coin(coins)
		m.start()
		sleep(run_time*3600)
		m.stop()
	
			
		
if __name__ == "__main__":
	coin_mining('ETH', run_time=1)
	coin_mining()

	
