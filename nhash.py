import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
from ConfigParser import SafeConfigParser 



CONFIG_FILE = 'config.txt'
NICEHASH_API_URL = "https://api.nicehash.com/api"
payload = {'method': 'simplemultialgo.info'}

OVERCLOCK_PROGRAM_BIN = "MSIAfterburner.exe"
OVERCLOCK_PROGRAM_PATH = "C:\Program Files (x86)\MSI Afterburner"



def get_algo_speed(algo='equihash'):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	benchmark = dict(cfg.items('BENCHMARK'))
	return int(benchmark[algo])


def read_algo():
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	algo_dict = dict(cfg.items('BENCHMARK'))
	algo_list = []
	for k in algo_dict:
		algo_list.append(k)
	return algo_list
 

def nicehash_best_algo():
	my_algo = read_algo()
	best_value = 0
	best_algo = ''
	req = requests.get(NICEHASH_API_URL, params=payload)
	reqResult = req.json()['result']
	rez =  reqResult['simplemultialgo']
	for i in rez:
		algo_name = i['name']
        if algo_name in my_algo:
            price = float(i["paying"])
            algo_speed = get_algo_speed(algo_name)
            algo_value = price*algo_speed
            if algo_value > best_value:
                best_value = algo_value
                best_algo = algo_name
	print datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M")
	print "CURRENT BEST ALGO: ", best_algo, "\n"
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


def start_mining(algo):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	miner_path = cfg.get(algo.upper(),'MINER_PATH')
	miner_bin = cfg.get(algo.upper(),'MINER_BIN')
	algo_file = algo.upper() + '.bat'
    try:
        os.chdir(miner_path)
        proc = Popen(algo_file, creationflags=CREATE_NEW_CONSOLE)
        print "[+] Successfully started mining on %s algorithm\n" %(algo)
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
        best_algo = get_best_algo()
        if CURRENT_ALGO != best_algo:
            CURRENT_ALGO = best_algo
            kill_process(current_miner)
            sleep(3)
            current_miner = start_mining(best_algo)
        sleep(300)





if __name__ == "__main__":
	print nicehash_best_algo()
	'''
    if not overclock_running():
        start_overclock()
    endless_miner()
    '''












