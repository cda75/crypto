# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 



WORK_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(WORK_DIR, 'config.txt')
BENCHMARK = os.path.join(WORK_DIR, 'benchmark.conf')
NICEHASH = os.path.join(WORK_DIR, 'nicehash.conf')


def nicehash_best_algo():
	cfg = SafeConfigParser()
	cfg.read(BENCHMARK)
	algo_dict = dict(cfg.items('DEFAULT'))
	my_algo = algo_dict.keys()
	print my_algo
	best_value = 0
	cfg.read(NICEHASH)
	API_URL = cfg.get('DEFAULT', 'API_URL')
	payload = {'method': cfg.get('DEFAULT', 'METHOD')}
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
	current_time = datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
	print "\n[%s] Current NiceHash Best Algo: %s" %(current_time, best_algo['name'])
	return best_algo


def kill_process(processName):
    cmdStr = "taskkill /f /im %s" %(processName)
    os.system(cmdStr)


def start_nicehash_mining(algo):
	cfg = SafeConfigParser()
	cfg.read(CONFIG)
	miner_bin = cfg.get('ALGO', algo['name'])
	cfg.read(NICEHASH)
	pool_url = cfg.get('DEFAULT', algo['name'])
	user = cfg.get('DEFAULT', 'ADDR')
	worker = cfg.get('DEFAULT', 'WORKER')
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
		print cmdStr
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


if __name__ == "__main__":
	endless_miner()
