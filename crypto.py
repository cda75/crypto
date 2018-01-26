# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 
import operator



WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(WORK_DIR, 'config.txt')
COINS = os.path.join(WORK_DIR, 'coins.conf')
BENCHMARK = os.path.join(WORK_DIR, 'benchmark.conf')
NICEHASH = os.path.join(WORK_DIR, 'nicehash.conf')
LOG = os.path.join(WORK_DIR, 'mining.log')
PID = os.path.join(WORK_DIR, 'PID')
COIN = os.path.join(WORK_DIR, 'COIN')


def logging(info):
	time = "[%s] " %datetime.strftime(datetime.now(), "%d/%m %H:%M:%S")
	print time+info
	with open(LOG, 'a') as f:
		f.write(time+info+'\n')


def kill_current_miner():
	pid = get_pid()
	cmdStr = "taskkill /f /im %s" %(pid)
	os.system(cmdStr)


def write_pid(pid):
	with open(PID, 'w') as f:
		f.write(pid)


def write_coin(coin):
	with open(COIN, 'w') as f:
		f.write(coin)


def get_pid():
	with open(PID) as f:
		pid = f.read()
	return pid


def check_pid(pid):
	if pid in Popen('tasklist', stdout=PIPE).communicate()[0]:
		return True
	else:
		return False


def get_best_coin():
	JSON_URL = r"https://whattomine.com/coins.json?utf8=✓&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=0&adapt_q_570=0&adapt_q_580=3&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=1&adapt_10606=true&adapt_q_1070=2&adapt_1070=true&adapt_q_1070Ti=1&adapt_1070Ti=true&adapt_q_1080=03&adapt_q_1080Ti=0&eth=true&factor%5Beth_hr%5D=113.0&factor%5Beth_p%5D=465.0&grof=true&factor%5Bgro_hr%5D=124.0&factor%5Bgro_p%5D=470.0&x11gf=true&factor%5Bx11g_hr%5D=43.4&factor%5Bx11g_p%5D=450.0&cn=true&factor%5Bcn_hr%5D=2320.0&factor%5Bcn_p%5D=360.0&eq=true&factor%5Beq_hr%5D=1600.0&factor%5Beq_p%5D=450.0&lre=true&factor%5Blrev2_hr%5D=132300.0&factor%5Blrev2_p%5D=470.0&ns=true&factor%5Bns_hr%5D=3550.0&factor%5Bns_p%5D=470.0&lbry=true&factor%5Blbry_hr%5D=1020.0&factor%5Blbry_p%5D=450.0&factor%5Bbk2b_hr%5D=5990.0&factor%5Bbk2b_p%5D=440.0&factor%5Bbk14_hr%5D=9100.0&factor%5Bbk14_p%5D=460.0&pas=true&factor%5Bpas_hr%5D=3580.0&factor%5Bpas_p%5D=450.0&skh=true&factor%5Bskh_hr%5D=104.5&factor%5Bskh_p%5D=450.0&factor%5Bl2z_hr%5D=420.0&factor%5Bl2z_p%5D=300.0&factor%5Bcost%5D=0.1&sort=Profit&volume=0&revenue=current&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=abucoins&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=bleutrade&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=Main&commit=Calculate"	
	cfg = SafeConfigParser()
	cfg.read(COINS)
	MY_COINS = cfg.sections()
	try:
		logging("[i] Checking best coin...")
		req = requests.get(JSON_URL)
		reqResult = req.json()['coins']
		best_dict = {}
		for coin, value in reqResult.iteritems():
			best_dict[coin] = value['profitability']
		rez = sorted(best_dict.items(), key=operator.itemgetter(1), reverse=True)
		for i in rez:
			coin_name = i[0]
			coin_tag = reqResult[coin_name]['tag']
			coin_algo = reqResult[coin_name]['algorithm']
			if coin_tag in MY_COINS:
				return coin_tag, coin_algo.lower()
	except ValueError:
		logging("Error getting info from WhatToMine....Mining ZEC")
		return 'ZEC', 'equihash'


def start_coin_mining(coin, algo):
	cfg = SafeConfigParser()
	cfg.read(CONFIG)
	miner_bin = cfg.get('ALGO', algo)
	cfg.read(COINS)
	user = cfg.get(coin, 'USER')
	addr = cfg.get(coin, 'ADDR')
	pool = cfg.get(coin, 'POOL')
	port = cfg.get(coin, 'PORT')
	worker = cfg.get(coin, 'WORKER')
	password = cfg.get(coin, 'PASSWORD')
	if algo == 'equihash':
		# EWBF Zcash CUDA miner
		cmdStr = "%s --server %s --port %s --user %s.%s --api 192.168.0.5:42000 --fee 0" %(miner_bin, pool, port, user, worker)
	elif algo == 'cryptonight':
		# XMR-STAK
		pass
	elif algo == 'ethash':
		# CLAYMOR DUAL miner
		dpool = cfg.get('ETH', 'DPOOL')
		dport = cfg.get('ETH', 'DPORT')
		duser = cfg.get('ETH', 'DUSER')
		dworker = cfg.get('ETH', 'DWORKER')
		dpassword = cfg.get('ETH', 'DPASSWORD')
		dcoin = cfg.get('ETH', 'DCOIN')
		cmdStr = "%s -epool %s:%s -ewal %s.%s -epsw %s -allcoins 1 -allpools 1 -dpool %s:%s -dwal %s.%s -dpsw %s -dcoin %s" %(miner_bin, pool, port, user, worker, password, dpool, dport, duser, dworker, dpassword, dcoin)
	else:
		# CCMINER
		cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo, pool, port, user, worker)
		#XVG
		#if coin == 'XVG':
		#	pool = cfg.get('XVG', algo)
		#	cmdStr = "%s -a %s -o %s -u %s.%s --cpu-priority=3" %(miner_bin, algo, pool, user, worker)
		#else:
		#	cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo, pool, port, user, worker)
	try:
		Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		pid = os.path.basename(miner_bin)
		write_pid(pid)
		write_coin(coin)
		logging("[+] Successfully started %s mining\n" %coin)
	except:
		logging("[-] ERROR starting %s miner\nExit\n" %coin)
		exit()


def coin_mining(t1=30, t2=12):
	logging("[i] Started coin mining")
	coin, algo = get_best_coin()
	logging("[i] My current most profitable coin is %s" %coin)
	start_coin_mining(coin, algo)
	for i in range(int(60/t1*t2)):
		sleep(t1*60)
		new_coin, new_algo = get_best_coin()
		if new_coin == coin:
			logging("[+] Continue mining %s\n" %coin)
		else:
			logging("[i] New most profitable coin is %s" %new_coin)
			kill_current_miner()
			sleep(5)
			logging("[+] Switching to mine %s" %new_coin)
			start_coin_mining(new_coin, new_algo)
			coin = new_coin
	kill_current_miner()
	logging("[+] Stop coin mining")
	logging("---------------------------------------------------------------------\n")


def nicehash_best_algo():
	cfg = SafeConfigParser()
	cfg.read(BENCHMARK)
	algo_dict = dict(cfg.items('DEFAULT'))
	my_algo = algo_dict.keys()
	best_value = 0
	cfg.read(NICEHASH)
	API_URL = cfg.get('DEFAULT', 'API_URL')
	payload = {'method': cfg.get('DEFAULT', 'METHOD')}
	try:
		logging("[i] Checking best algo...")
		req = requests.get(API_URL, params=payload)
		reqResult = req.json()['result']
		rez =  reqResult['simplemultialgo']
		for i in rez:
			algo_name = i['name'].strip()
			if algo_name in my_algo:
				algo_price = float(i["paying"])
				algo_speed = long(algo_dict[algo_name])
				algo_value = algo_price*algo_speed
				if algo_value > best_value:
					best_value = algo_value
					best_algo = i
		return best_algo
	except ValueError:
		logging('[-] Oooops. Error getting data from NiceHash\nMining on Equihash algo')
		return 'equihash'


def start_nicehash_mining(algo):
	cfg = SafeConfigParser()
	cfg.read(CONFIG)
	miner_bin = cfg.get('ALGO', algo['name'])
	cfg.read(NICEHASH)
	pool = cfg.get('DEFAULT', algo['name'])
	user = cfg.get('DEFAULT', 'ADDR')
	worker = cfg.get('DEFAULT', 'WORKER')
	port = algo['port']
	if algo['name'] == 'equihash':
		# EWBF Zcash CUDA miner
		cmdStr = "%s --server %s --port %s --user %s.%s --api 192.168.0.5:42000 --fee 0" %(miner_bin, pool, port, user, worker)
	elif algo['name'] == 'cryptonight':
		# XMR-STAK
		pass
	elif algo['name'] == 'ethash':
		# CLAYMOR DUAL miner
		cmdStr = "%s -epool %s:%s -ewal %s.%s -epsw %s" %(miner_bin, pool, port, user, worker, password)
	else:
		# CCMINER
		cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo['name'], pool, port, user, worker)
	try:
		Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		logging("[+] Successfully started mining on %s algorithm\n" %(algo['name']))
		pid = os.path.basename(miner_bin)
		write_pid(pid)
		write_coin(algo['name'].upper())
	except:
		logging("[-] ERROR starting miner %s\nExit" %cmdStr)
		exit()


def nicehash_mining(t1=2, t2=12):
	logging("[i] Started NiceHash mining")
	best_algo = nicehash_best_algo()
	logging("[i] Current NiceHash best algo: %s" %(best_algo['name']))
	start_nicehash_mining(best_algo)
	for i in range(int(60/t1*t2)):
		sleep(t1*60)
		new_algo = nicehash_best_algo()
		if new_algo['name'] == best_algo['name']:
			logging("[i] Continue on current algo %s" %best_algo['name'])
		else:
			logging("[i] New NiceHash best algo is %s" %new_algo['name'])
			kill_current_miner()
			sleep(5)
			logging("[+] Switching to mine on %s algo\n" %new_algo['name'])
			start_nicehash_mining(new_algo)
			best_algo = new_algo
	kill_current_miner()
	logging("[+] Stop nicehash mining")
	logging("----------------------------------------------------------------------\n")


if __name__ == "__main__":
	while True:
		coin_mining()
		nicehash_mining()



