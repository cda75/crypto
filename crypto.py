# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 


WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(WORK_DIR, 'config.txt')


def nicehash_best_algo():
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	algo_dict = dict(cfg.items('BENCHMARK'))
	my_algo = algo_dict.keys()
	best_value = 0
	NICEHASH_API_URL = cfg.get('NICEHASH', 'API_URL')
	payload = {'method': cfg.get('NICEHASH', 'METHOD')}
	req = requests.get(NICEHASH_API_URL, params=payload)
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
				best_algo = algo_name
				algo_port = i['port']
	current_time = datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
	print "\n[%s] Current NiceHash Best Algo: %s" %(current_time, best_algo)
	return best_algo, algo_port


def kill_process(processName):
    cmdStr = "taskkill /f /im %s" %(processName)
    os.system(cmdStr)


def overclock_running():
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	oc_prog = os.path.basename(cfg.get('OVERCLOCK','PATH'))
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == oc_prog:
			return True
	return False


def start_overclock(profile=1):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	oc_prog = os.path.abspath(cfg.get('OVERCLOCK','PATH'))
	cmdStr = "%s \s -Profile%s" %(oc_prog, profile)
	Popen(cmdStr)
	sleep(5)


def start_nicehash_mining(algo, port):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	miner_bin = cfg.get(algo.upper(),'MINER_BIN')
	pool_url = cfg.get('NICEHASH', algo)
	user = cfg.get('NICEHASH', 'ADDR')
	worker = cfg.get('NICEHASH', 'WORKER')
	if algo == 'equihash':
		# EWBF Zcash CUDA miner
		cmdStr = "%s --server %s --port %s --user %s.%s --fee 0" %(miner_bin, pool_url, port, user, worker)
	elif algo == 'cryptonight':
		# XMR-STAK
		pass
	elif algo == 'ethash':
		# CLAYMOR DUAL miner
		print 'Not ready yet'
		pass
	else:
		# CCMINER
		cmdStr = "%s -a %s -o stratum+tcp://%s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo, pool_url, port, user, worker)
	try:
		proc = Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		print "[+] Successfully started mining on %s algorithm\n" %(algo)
		sleep(3)
		return os.path.basename(miner_bin)
	except:
		print "[-] ERROR starting miner"
		return False


def endless_miner():
    best_algo, port = nicehash_best_algo()
    current_miner = start_nicehash_mining(best_algo, port)
    CURRENT_ALGO = best_algo
    sleep(60)
    while True:    
        best_algo, port = nicehash_best_algo()
        if CURRENT_ALGO != best_algo:
            CURRENT_ALGO = best_algo
            kill_process(current_miner)
            sleep(3)
            current_miner = start_nicehash_mining(best_algo, port)
        sleep(100)


def whattomine_best_coin():
	'''
	Calculate the best profit for coin from mining pool
	H 		= 	your equipment hashrate
	NH 		= 	pool total hashrate
	BpH 	= 	block per hour from pool statistic
	D 		=	network difficulty
	BR 		=	block reward
	P 		=	price in USD

	Reward in hour (in coins) = H*BpH*BR/NH
	Reward in hour (in USD$) = (Reward in coins) * P
	API_URL = https://api-zcash.flypool.org/poolStats
	NH = data['poolstats']['hashRate']
	BpH = data['poolstats']['blocksPerHour']
	P = data['price']['usd']

	'''
	API_URL = 'http://whattomine.com/coins.json'
	req = requests.get(API_URL)
	reqResult = req.json()['coins']
	coins = reqResult.keys()
	profit = 0
	for coin, value in reqResult.iteritems():
		if value["profitability"] > profit:
			profit = value["profitability"]
			best_coin = coin
		if coin == 'Zcash':
			N = float(value["nethash"])
			H = 1300
			HR = H/N
			BR = value["block_reward"]
			E = float(86400*BR/150)
			D = value["difficulty"]
			R = HR*E
	print best_coin, profit
	print R


def get_flypool_profit(coin, hashrate):
	FLYPOOL_API_URL = "https://api-zcash.flypool.org/poolStats"
	req = requests.get(FLYPOOL_API_URL)
	data = req.json()['data']
	PF = 0.99
	NH = data['poolStats']['hashRate']
	BpH = data['poolStats']['blocksPerHour']
	profit = get_coin_profit(coin, hashrate, NH, BpH)
	return profit*PF


def get_coin_profit(coin, HR, NH, BpH):
	BR = get_block_reward(coin)
	P = get_coin_price(coin,'usd')
	profit = HR*BpH*BR*P/NH
	return profit


def get_coin_price(coin, cur):
	cur = cur.upper()
	coin = coin.upper()
	API_URL = "https://min-api.cryptocompare.com/data/price?"
	payload = {'fsym': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	result = req.json()[cur] 
	return result


def get_block_reward(coin):
	coin = coin.upper()
	rewards = {'ZEC':10.0, 'XMR':5.8, 'XVG':1560.0}
	return rewards[coin]

def get_best_coin():
	pass


def start_mining_coin(coin):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)


def main():
	if not overclock_running():
		start_overclock()
	endless_miner()



if __name__ == "__main__":
	print get_coin_price('zec', 'usd')
	print get_block_reward('zec')
	print get_flypool_profit('zec',1300)*24


	#main()













