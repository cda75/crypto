# -*- coding: utf-8 -*-

import requests
from time import sleep
import os
from ConfigParser import SafeConfigParser 
import json
import pandas as pd
from flask import Flask, render_template
from datetime import datetime
import csv
from operator import itemgetter
import tablib
import threading


WORK_DIR = os.path.dirname(os.path.realpath(__file__))
COINS = os.path.join(WORK_DIR, 'coins.conf')
API = os.path.join(WORK_DIR, 'api.conf')
PRICES = os.path.join(WORK_DIR, 'price.csv')

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
def main():
	dataset = tablib.Dataset()
	with open(PRICES) as f:
		dataset.csv = f.read()
	data = dataset.html
	return render_template('index.html', data=data)


@app.route('/mrk1.html')
def market():
	dataset = tablib.Dataset()
	with open(PRICES) as f:
		dataset.csv = f.read()
	data = dataset.html
	return render_template('mrk1.html', data=data)


@app.route('/balance.html')
def balance():

	return render_template('balance.html')


@app.route('/dt.html')
def date_time():
	date = dt.strftime(dt.now(), "%d/%m/%Y")
	time = dt.strftime(dt.now(), "%H:%M:%S")
	return render_template('dt.html', date=date, time=time, uptime='uptime')


def get_current_coin():
	with open(COIN, 'r') as f:
		return f.read()


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
			header = ['COIN','USD','RUB','BTC']
			with open(PRICES, 'wb') as f:
				writer = csv.writer(f)
				writer.writerow(header)
				for row in prices:
					writer.writerow(row)
			sleep(self.interval)


def main():
	pass


if __name__ == "__main__":
	MarketData()
	app.run(debug = True)



