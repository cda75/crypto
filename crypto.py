# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 
import operator



WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(WORK_DIR, 'config.txt')
COINS = os.path.join(WORK_DIR, 'coins.conf')


def kill_process(processName):
	cmdStr = "taskkill /f /im %s" %(processName)
	os.system(cmdStr)


def get_best_coin():
	JSON_URL = r"https://whattomine.com/coins.json?utf8=✓&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=0&adapt_q_570=0&adapt_q_580=3&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=1&adapt_10606=true&adapt_q_1070=2&adapt_1070=true&adapt_q_1070Ti=1&adapt_1070Ti=true&adapt_q_1080=03&adapt_q_1080Ti=0&eth=true&factor%5Beth_hr%5D=113.0&factor%5Beth_p%5D=465.0&grof=true&factor%5Bgro_hr%5D=124.0&factor%5Bgro_p%5D=470.0&x11gf=true&factor%5Bx11g_hr%5D=43.4&factor%5Bx11g_p%5D=450.0&cn=true&factor%5Bcn_hr%5D=2320.0&factor%5Bcn_p%5D=360.0&eq=true&factor%5Beq_hr%5D=1600.0&factor%5Beq_p%5D=450.0&lre=true&factor%5Blrev2_hr%5D=132300.0&factor%5Blrev2_p%5D=470.0&ns=true&factor%5Bns_hr%5D=3550.0&factor%5Bns_p%5D=470.0&lbry=true&factor%5Blbry_hr%5D=1020.0&factor%5Blbry_p%5D=450.0&factor%5Bbk2b_hr%5D=5990.0&factor%5Bbk2b_p%5D=440.0&factor%5Bbk14_hr%5D=9100.0&factor%5Bbk14_p%5D=460.0&pas=true&factor%5Bpas_hr%5D=3580.0&factor%5Bpas_p%5D=450.0&skh=true&factor%5Bskh_hr%5D=104.5&factor%5Bskh_p%5D=450.0&factor%5Bl2z_hr%5D=420.0&factor%5Bl2z_p%5D=300.0&factor%5Bcost%5D=0.1&sort=Profit&volume=0&revenue=current&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=abucoins&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=bleutrade&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=Main&commit=Calculate"	
	'''
	Calculate the best profit for coin from mining pool
	H 		= 	your equipment hashrate
	NH 		= 	pool total hashrate
	BpH 	= 	blocks per hour from pool statistic or Estimated Average Pool Round Time
	BR 		=	block reward
	P 		=	price in USD

	Reward in hour (in coins) = H*BpH*BR/NH
	Reward in hour (in USD$) = (Reward in coins) * P
	'''
	cfg = SafeConfigParser()
	cfg.read(COINS)
	MY_COINS = cfg.sections()
	req = requests.get(JSON_URL)
	reqResult = req.json()['coins']
	profit = 0
	best_dict = {}
	for coin, value in reqResult.iteritems():
		best_dict[value['tag']] = value['profitability']
		if value["profitability"] > profit:
			profit = value["profitability"]
			best_coin = value['tag']
			algo = value['algorithm']
	print "Current best coin %s with %s" %(best_coin, algo) 
	rez = sorted(best_dict.items(), key=operator.itemgetter(1), reverse=True)
	for i in rez:
		best_coin = i[0]
		if best_coin in MY_COINS:
			return best_coin


def start_mining_coin(coin):
	cfg = SafeConfigParser()
	cfg.read(COINS)
	algo = cfg.get(coin, 'ALGO')
	user = cfg.get(coin, 'USER')
	addr = cfg.get(coin, 'ADDR')
	pool = cfg.get(coin, 'POOL')
	port = cfg.get(coin, 'PORT')
	worker = cfg.get(coin, 'WORKER')
	password = cfg.get(coin, 'PASSWORD')
	cfg.read(CONFIG)
	miner_bin = cfg.get('ALGO', algo)
	if algo == 'equihash':
		# EWBF Zcash CUDA miner
		cmdStr = "%s --server %s --port %s --user %s.%s --api 0.0.0.0:42000 --fee 0" %(miner_bin, pool, port, user, worker)
	elif algo == 'cryptonight':
		# XMR-STAK
		pass
	elif algo == 'ethash':
		# CLAYMOR DUAL miner
		cmdStr = "%s -epool %s:%s -ewal %s.%s -epsw %s" %(miner_bin, pool, port, user, worker, password)
	else:
		# CCMINER
		cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo, pool, port, user, worker)
	try:
		proc = Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		print datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
		print "[+] Successfully started mining %s on %s algorithm\n" %(coin, algo.upper())
		sleep(3)
		return os.path.basename(miner_bin)
	except:
		print "[-] ERROR starting %s miner" %coin
		return False

	print 'Started mining coin %s' %coin



if __name__ == "__main__":
	best_coin = get_best_coin()
	process = start_mining_coin(best_coin)
	while True:
		sleep(900)
		new_coin = get_best_coin()
		if new_coin != best_coin:
			best_coin = new_coin
			kill_process(process)
			sleep(5)
			process = start_mining_coin(best_coin)
