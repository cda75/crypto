import requests
import os
from datetime import datetime
from time import sleep
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil


MY_ALGO = [8,9,24,28,29]
BENCHMARK = {	"8": {"speed": 2800000},
				"9": {"speed": 116000000},
				"24": {"speed": 1290},
				"28": {"speed": 11400000000},
				"29": {"speed": 91000000}
			}

ALGO = {"8": {"algo": 8, "name": "neoscrypt", "url": "neoscrypt.eu.nicehash.com:3341", "path": "C:\\Users\\root\\CryptoPro\\ccminer", "bin": "ccminer-x64.exe"},
    "9": {"algo": 9, "name": "lyra2rev2", "url": "lyra2rev2.eu.nicehash.com:3347", "path": "C:\\Users\\root\\CryptoPro\\ccminer", "bin": "ccminer-x64.exe"},
    "24": {"algo": 24, "name": "equihash", "url": "equihash.eu.nicehash.com:3357", "path": "C:\\Users\\root\\CryptoPro\\ewbf", "bin": "miner.exe"},
    "28": {"algo": 28, "name": "blake2c", "url": "blake2s.eu.nicehash.com:3361", "path": "C:\\Users\\root\\CryptoPro\\ccminer", "bin": "ccminer-x64.exe"},
    "29": {"algo": 29, "name": "skunk", "url": "skunk.eu.nicehash.com:3362", "path": "C:\\Users\\root\\CryptoPro\\ccminer", "bin": "ccminer-x64.exe"}
    }
    
API_URL = "https://api.nicehash.com/api"
payload = {'method': 'simplemultialgo.info'}


def get_best_algo():
    best_value = 0
    best_algo = ''
    req = requests.get(API_URL, params=payload)
    reqResult = req.json()['result']
    rez =  reqResult['simplemultialgo']
    for i in rez:
        if i["algo"] in MY_ALGO:
            k = str(i["algo"])
            price = float(i["paying"])
#            speed = x[k]['speed']
            algo_value = price*BENCHMARK[k]["speed"]
            if algo_value > best_value:
                best_value = algo_value
                best_algo = k
    print datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M")
    print "CURRENT BEST ALGO: ", ALGO[best_algo]['name'], "\n"
    return ALGO[best_algo]


def kill_proc(name):
    cmd_str = 'taskkill /f /im ' + name
    os.system(cmd_str)


def overclock_running():
    name = "MSIAfterburner.exe"
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == name:
            return True
    return False


def start_overclock():
    path = "C:\Program Files (x86)\MSI Afterburner"
    os.chdir(path)
    Popen("MSIAfterburner.exe \s -Profile1")
    sleep(5)


def start_mining(algo):
    algo_file = str(algo["name"]).upper() + '.bat'
    try:
        os.chdir(algo["path"])
        proc = Popen(algo_file, creationflags=CREATE_NEW_CONSOLE)
        print "Successfully started mining on %s algorithm\n" %(algo['name'])
        sleep(3)
        return algo['bin']
    except:
        print "ERROR"


def endless_miner():
    best_algo = get_best_algo()
    process = start_mining(best_algo)
    CURRENT_ALGO = best_algo["algo"]
    sleep(60)
    while True:    
        best_algo = get_best_algo()
        if CURRENT_ALGO != best_algo["algo"]:
            CURRENT_ALGO = best_algo["algo"]
            kill_proc(process)
            sleep(3)
            process = start_mining(best_algo)
        sleep(300)





if __name__ == "__main__":
    if not overclock_running():
        start_overclock()
    endless_miner()











