# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
#from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 
import operator



WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(WORK_DIR, 'config.txt')
MY_COINS = ['ZEC','ZCL','XMR', 'XVG-LYRA2V2', 'HUSH']

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
				best_algo = i
	current_time = datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
	print "\n[%s] Current NiceHash Best Algo: %s" %(current_time, best_algo['name'])
	return best_algo


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


def start_nicehash_mining(algo):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	miner_bin = cfg.get(algo['name'].upper(),'MINER_BIN')
	pool_url = cfg.get('NICEHASH', algo['name'])
	user = cfg.get('NICEHASH', 'ADDR')
	worker = cfg.get('NICEHASH', 'WORKER')
	port = algo['port']
	if algo['name'] == 'equihash':
		# EWBF Zcash CUDA miner
		cmdStr = "%s --server %s --port %s --user %s.%s --fee 0" %(miner_bin, pool_url, port, user, worker)
	elif algo['name'] == 'cryptonight':
		# XMR-STAK
		pass
	elif algo['name'] == 'ethash':
		# CLAYMOR DUAL miner
		print 'Not ready yet'
		pass
	else:
		# CCMINER
		cmdStr = "%s -a %s -o %s:%s -u %s.%s --cpu-priority=3" %(miner_bin, algo['name'], pool_url, port, user, worker)
	try:
		proc = Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		print "[+] Successfully started mining on %s algorithm\n" %(algo['name'])
		sleep(3)
		return os.path.basename(miner_bin)
	except:
		print "[-] ERROR starting miner"
		return False


def get_nicehash_stat(algo_id):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	API_URL = cfg.get('NICEHASH', 'API_URL')
	method = 'stats.provider.workers'
	ADDR = cfg.get('NICEHASH', 'ADDR')
	payload = {'method':method, 'addr':ADDR, 'algo':algo_id}
	req = requests.get(API_URL, params=payload)
	reqResult = req.json()['result']
	workers = reqResult['workers']
	return workers[1]['a']


def endless_miner():
    best_algo = nicehash_best_algo()
    CURRENT_ALGO = best_algo['name']
    current_miner = start_nicehash_mining(best_algo)
    sleep(60)
    while True:    
        best_algo = nicehash_best_algo()
        if CURRENT_ALGO != best_algo['name']:
            CURRENT_ALGO = best_algo['name']
            kill_process(current_miner)
            sleep(3)
            current_miner = start_nicehash_mining(best_algo)
        sleep(60)


def whattomine_best_coin():
        JSON_URL = "https://whattomine.com/coins.json?utf8=✓&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=0&adapt_q_570=0&adapt_q_580=3&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=1&adapt_10606=true&adapt_q_1070=2&adapt_1070=true&adapt_q_1070Ti=1&adapt_1070Ti=true&adapt_q_1080=03&adapt_q_1080Ti=0&eth=true&factor%5Beth_hr%5D=113.0&factor%5Beth_p%5D=465.0&grof=true&factor%5Bgro_hr%5D=124.0&factor%5Bgro_p%5D=470.0&x11gf=true&factor%5Bx11g_hr%5D=43.4&factor%5Bx11g_p%5D=450.0&cn=true&factor%5Bcn_hr%5D=2320.0&factor%5Bcn_p%5D=360.0&eq=true&factor%5Beq_hr%5D=1600.0&factor%5Beq_p%5D=450.0&lre=true&factor%5Blrev2_hr%5D=132300.0&factor%5Blrev2_p%5D=470.0&ns=true&factor%5Bns_hr%5D=3550.0&factor%5Bns_p%5D=470.0&lbry=true&factor%5Blbry_hr%5D=1020.0&factor%5Blbry_p%5D=450.0&factor%5Bbk2b_hr%5D=5990.0&factor%5Bbk2b_p%5D=440.0&factor%5Bbk14_hr%5D=9100.0&factor%5Bbk14_p%5D=460.0&pas=true&factor%5Bpas_hr%5D=3580.0&factor%5Bpas_p%5D=450.0&skh=true&factor%5Bskh_hr%5D=104.5&factor%5Bskh_p%5D=450.0&factor%5Bl2z_hr%5D=420.0&factor%5Bl2z_p%5D=300.0&factor%5Bcost%5D=0.1&sort=Profit&volume=0&revenue=current&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=abucoins&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=bleutrade&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=Main&commit=Calculate"	
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
        print best_coin, algo 
	rez = sorted(best_dict.items(), key=operator.itemgetter(1), reverse=True)
        for i in rez:
            best_coin = i[0]
            if best_coin in MY_COINS:
                return best_coin


def get_ZEC_profit(hashrate):
	FLYPOOL_API_URL = "https://api-zcash.flypool.org/poolStats"
	req = requests.get(FLYPOOL_API_URL)
	data = req.json()['data']
	PF = 0.99
	NH = data['poolStats']['hashRate']
	BpH = data['poolStats']['blocksPerHour']
	profit = get_coin_profit('ZEC', hashrate, NH, BpH)
	return profit


def get_XVG_profit(hashrate):
	API_URL = "http://xvg-lyra.idcray.com/index.php?"
	payload = {'page': 'api', 'action':'getpoolstatus', 'api_key': 'e427e3be81c79df098d074e351902bb1b210574a4fd6d641f42b74a0baafb7df'}
	req = requests.get(API_URL, params=payload)
	data = req.json()[payload['action']]['data']
	NH = data["hashrate"]
	BpH = 3600/data['esttime']
	profit = get_coin_profit('XVG', hashrate, NH, BpH)
	return profit


def get_ZCL_profit(hashrate):
	API_URL = "https://zclassic.miningpoolhub.com/"
	payload = {'page': 'api', 'action':'getpoolstatus', 'api_key': 'cfdbe7a47bcdcb088d0e11aee243679963c1806f74861136c2b7043a6a89e4a5'}
	req = requests.get(API_URL, params=payload)
	data = req.json()[payload['action']]['data']
	NH = data["hashrate"]
	BpH = 3600/data['esttime']
	profit = get_coin_profit('ZCL', hashrate, NH, BpH)
	return profit


def get_coin_profit(coin, HR, NH, BpH):
	BR = get_coin_data(coin)[0]
	P = get_coin_price(coin,'usd')
	usd_profit = HR*BpH*BR*P/NH
	coin_profit = HR*BpH*BR/NH
	return 24*usd_profit, 24*coin_profit


def get_coin_price(coin, cur):
	cur = cur.upper()
	coin = coin.upper()
	API_URL = "https://min-api.cryptocompare.com/data/price?"
	payload = {'fsym': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	result = req.json()[cur] 
	return result


def get_coin_data(coin):
	coin = coin.upper()
	URL = "http://whattomine.com/coins.json"
	req = requests.get(URL)
	data = req.json()['coins'].values() 
	for v in data:
		if v["tag"] == coin:
			block_reward = v["block_reward"]
			block_time = float(v["block_time"])
			algo = v["algorithm"]
			profit = v["profitability"]
			nethash = v["nethash"]
			diff = v["difficulty"]
	return block_reward, block_time, profit



def get_best_coin():
	pass


def start_mining_coin(coin):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
        print 'Started mining coin %s' %coin
        pass


def main():
	if not overclock_running():
		start_overclock()
	endless_miner()



if __name__ == "__main__":
#	main()
        best_coin = whattomine_best_coin()
        start_mining_coin(best_coin)
        



