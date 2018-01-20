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
	return best_algo


def kill_process(processName):
	cmdStr = "taskkill /f /im %s" %(processName)
	os.system(cmdStr)


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
		cmdStr = "%s --server %s --port %s --user %s.%s --api 127.0.0.1:42000 --fee 0" %(miner_bin, pool, port, user, worker)
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
		proc = Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		current_time = datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
		print "\n[%s] Current NiceHash Best Algo: %s" %(current_time, best_algo['name'])
		print "[+] Successfully started mining on %s algorithm\n" %(algo['name'])
		sleep(3)
		return os.path.basename(miner_bin)
	except:
		print "[-] ERROR starting miner"
		return False


def get_nicehash_stat(algo_id):
	if algo_id in [8,14,29]:
		unit = 'MH/s'
	elif algo_id in [23,28]:
		unit = 'GH/s'
	else:
		unit = 'H/s'
	cfg = SafeConfigParser()
	cfg.read(NICEHASH)
	API_URL = cfg.get('DEFAULT', 'API_URL')
	method = 'stats.provider.workers'
	ADDR = cfg.get('DEFAULT', 'ADDR')
	payload = {'method':method, 'addr':ADDR, 'algo':algo_id}
	req = requests.get(API_URL, params=payload)
	reqResult = req.json()['result']
	workers = reqResult['workers']
	hash_speed = str(workers[0][1]['a'])
	print "%s %s" %(hash_speed, unit)



if __name__ == "__main__":
	best_algo = nicehash_best_algo()
	current_miner = start_nicehash_mining(best_algo)
	while True:
		for i in range(3):
			sleep(60)
			get_nicehash_stat(best_algo['algo'])
		new_algo = nicehash_best_algo()
		if new_algo['name'] != best_algo['name']:
			best_algo = new_algo
			kill_process(current_miner)
			sleep(5)
			current_miner = start_nicehash_mining(best_algo)

