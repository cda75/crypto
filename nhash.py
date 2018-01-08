# -*- coding: utf-8 -*-

import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 


CONFIG_DIR = r"C:\Users\root\CryptoPro\Function"
CONFIG_FILE = "config.txt"

OVERCLOCK_PROGRAM_BIN = "MSIAfterburner.exe"
OVERCLOCK_PROGRAM_PATH = "C:\Program Files (x86)\MSI Afterburner"



def nicehash_best_algo():
	cfg = SafeConfigParser()
	cFile = os.path.join(CONFIG_DIR,CONFIG_FILE)
	cfg.read(cFile)
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
	current_time = datetime.strftime(datetime.now(), "%d.%m.%y %H:%M")
	print "\n[%s] Current Best Algo: %s" %(current_time, best_algo)
	return best_algo


def kill_process(processName):
    cmdStr = "taskkill /f /im %s" %(processName)
    os.system(cmdStr)


def overclock_running():
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == OVERCLOCK_PROGRAM_BIN:
            return True
    return False


def start_overclock(profile=1):
    os.chdir(OVERCLOCK_PROGRAM_PATH)
    cmdStr = "%s \s -Profile%s" %(OVERCLOCK_PROGRAM_BIN, profile)
    Popen(cmdStr)
    sleep(5)


def start_mining(coin):
	cfg = SafeConfigParser()
	cFile = os.path.join(CONFIG_DIR,CONFIG_FILE)
	cfg.read(cFile)
	algo = cfg.get(coin, 'ALGO')
	miner_path = cfg.get(algo.upper(),'MINER_PATH')
	miner_bin = cfg.get(algo.upper(),'MINER_BIN')
#	algo_file = algo.upper() + '.bat'
	if algo == 'equihash':
		pool_url = cfg.get(coin, 'POOL')
		pool_user = cfg.get(coin, 'USER')
		pool_password = cfg.get(coin, 'PASSWORD')
		port = cfg.get(coin, 'PORT')
		api = cfg.get('MAIN', 'IP')
		cmdStr = "%s --server %s --user %s --pass %s --port %s --api %s --fee 0" %(miner_bin, pool_url, pool_user, pool_password, port, api)
	else:
		cmdStr = "%s -a %s -o %s -u %s.rig1" %(miner_bin, algo, pool_url, addr)
	try:
		os.chdir(miner_path)
		proc = Popen(cmdStr, creationflags=CREATE_NEW_CONSOLE)
		print "[+] Successfully started mining on %s algorithm\n" %(algo)
		proc = Popen(algo_file, creationflags=CREATE_NEW_CONSOLE)
		print "[+] Successfully started mining on %s algorithm" %(algo)
		sleep(3)
		return miner_bin
	except:
		print "[-] ERROR starting miner"


def endless_miner():
    best_algo = nicehash_best_algo()
    current_miner = start_mining(best_algo)
    CURRENT_ALGO = best_algo
    sleep(60)
    while True:    
        best_algo = nicehash_best_algo()
        if CURRENT_ALGO != best_algo:
            CURRENT_ALGO = best_algo
            kill_process(current_miner)
            sleep(3)
            current_miner = start_mining(best_algo)
        sleep(300)


def main():
	if not overclock_running():
		start_overclock()
	endless_miner()



if __name__ == "__main__":
	main()
    












