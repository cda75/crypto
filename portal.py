# -*- coding: utf-8 -*-

import requests
from time import sleep, time
import os
from ConfigParser import SafeConfigParser 
import json
from flask import Flask, render_template
from datetime import datetime as dt
import csv
from operator import itemgetter
import threading
from subprocess import Popen
import psutil


WORK_DIR = os.path.dirname(os.path.realpath(__file__))
COINS = os.path.join(WORK_DIR, 'coins.conf')
API = os.path.join(WORK_DIR, 'api.conf')
PRICES = os.path.join(WORK_DIR, 'price.csv')
BALANCE = os.path.join(WORK_DIR, 'balance.csv')
PID = os.path.join(WORK_DIR, 'PID')
COIN = os.path.join(WORK_DIR, 'COIN')

app = Flask(__name__)

ALGO = {'ETH': 'Ethash',
		'ETC': 'Ethash',
		'ZEC': 'Equihash',
		'ZCL': 'Equihash',
		'KMD': 'Equihash',
		'BTG': 'Equihash',
		'ZEN': 'Equihash',
		'HUSH': 'Equihash',
		'XVG': 'X17',
		'XMR': 'Cryptonight'
}


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/main.html')
def main():
	stat = dict()
	stat['coin'] = get_current_coin()
	#stat['algo'] = ALGO[stat['coin']]
	proc_name = get_process_name()
	stat['process_name'] = proc_name
	stat['uptime'] = get_process_uptime(proc_name)

	'''
	if (stat['algo'] == 'Ethash' and stat['pid'] == "EthDcrMiner64.exe"):
		stat['status'] = 'ACTIVE'
	elif stat['algo'] in ['x17','neoscrypt','lyra2rev2'] and stat['pid'] == "ccminer-x64.exe":
		stat['status'] = 'ACTIVE'
	elif stat['algo'] == 'Equihash' and stat['pid'] == "zm.exe":
		stat['status'] = 'ACTIVE'
	else:
		stat['status'] = 'INACTIVE'
		'''
	return render_template('main.html', stat=stat)


@app.route('/market.html')
def market():
	API = "https://min-api.cryptocompare.com/data/pricemulti"
	MY_COINS = 'BTC,ETH,ETC,ZEC,ZCL,XMR,XVG,KMD,HUSH'
	MY_CUR = 'USD,RUB,BTC'
	payload = {'fsyms': MY_COINS, 'tsyms': MY_CUR}
	req = requests.get(API, params=payload)
	r = req.json()
	rez = []
	for k,v in r.iteritems():
		rez.append([k,v['USD'],v['RUB'],v['BTC']])
	prices = sorted(rez, key=itemgetter(0))
	return render_template('market.html', data=prices)



@app.route('/balance.html')
def balance():
	return render_template('balance.html')


@app.route('/dt.html')
def date_time():
	date = dt.strftime(dt.now(), "%d/%m/%Y")
	time = dt.strftime(dt.now(), "%H:%M:%S")
	return render_template('dt.html', date=date, time=time)


@app.route('/log.html')
def log():
	return render_template('log.html')


def get_current_coin():
	with open(COIN, 'r') as f:
		return f.read()


def get_process_name():
	with open(PID, 'r') as f:
		return f.read()


def check_pid(pid):
	if pid in Popen('tasklist', stdout=PIPE).communicate()[0]:
		return True
	else:
		return False

def get_pid_by_name(process_name):
	for process in psutil.process_iter():
		if process_name.lower() == process.name().lower():
			return process.pid

def get_process_uptime(process_name):
	for process in psutil.process_iter():
		if process_name.lower() == process.name().lower():
			create_time = process.create_time()
			now = time()
			diff = int(now - create_time)
			m, s = divmod(diff,60)
			h, m = divmod(m,60)
			return "%02d:%02d:%02d" %(h,m,s)


def get_balance(coin):
	requests.packages.urllib3.disable_warnings()
	cfg = SafeConfigParser()
	cfg.read(API)
	if coin == "BTC":
		url = cfg.get(coin, 'BALANCE')
		req = requests.get(url)
		value = float(req.json())/10**8
	elif coin == "ZEC":
		url = cfg.get(coin, 'BALANCE')
		req = requests.get(url)
		value = float(req.json()['balance'])
	elif coin == 'XVG':
		url = cfg.get(coin, 'BALANCE')
		req = requests.get(url, verify=False)
		value = float(req.json())
	elif coin in ['ZCL', 'KMD', 'HUSH']:
		url = cfg.get(coin, 'API_URL')
		api_key = cfg.get(coin, 'API_KEY')
		arg = cfg.get(coin, 'USER_ID')
		payload = {'page': 'api', 'action': 'getusertransactions', 'api_key': api_key}
		req = requests.get(url, params=payload)
		print req.url
		value = 0
		tx = req.json()['getusertransactions']['data']['transactions']
		for i in tx:
			if 'Debit' in i['type']:
				value +=i['amount']
	return value


class MarketData(object):
	def __init__(self, interval=60):
		self.interval = interval
		self.API = "https://min-api.cryptocompare.com/data/pricemulti"
		self.MY_COINS = 'BTC,ETH,ETC,ZEC,ZCL,XMR,XVG,KMD,HUSH'
		self.MY_CUR = 'USD,RUB,BTC'
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                         
		thread.start()
	def run(self):
		while True:
			payload = {'fsyms': self.MY_COINS, 'tsyms': self.MY_CUR}
			req = requests.get(self.API, params=payload)
			r = req.json()
			rez = []
			for k,v in r.iteritems():
				rez.append([k,v['USD'],v['RUB'],v['BTC']])
			prices = sorted(rez, key=itemgetter(0))
			header = ['Монета','Стоимость в USD','Стоимость в RUB','Стоимость в BTC']
			with open(PRICES, 'wb') as f:
				writer = csv.writer(f)
				writer.writerow(header)
				for row in prices:
					writer.writerow(row)
			sleep(self.interval)




if __name__ == "__main__":
	#MarketData()
	app.run(host="0.0.0.0", debug = True)



