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
#API = os.path.join(WORK_DIR, 'api.conf')
PRICES = os.path.join(WORK_DIR, 'price.csv')
BALANCE = os.path.join(WORK_DIR, 'balance.csv')
PID = os.path.join(WORK_DIR, 'PID')
COIN = os.path.join(WORK_DIR, 'COIN')

MY_COINS = ['BTC','ETH','ETC','ZEC','XVG','ZCL','XMR','KMD','HUSH']

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/main.html')
def main():
	stat = dict()
	stat['coin'] = get_current_coin()
	proc_name = get_process_name()
	stat['process_name'] = proc_name
	stat['uptime'] = get_process_uptime(proc_name)
	return render_template('main.html', stat=stat)


@app.route('/market.html')
def market():
	prices = get_market_prices()
	return render_template('market.html', data=prices)


@app.route('/balance.html')
def balance():
	balance = []
	total = dict()
	total['USD'] = 0
	total['RUB'] = 0
	total['BTC'] = 0
	for coin in MY_COINS:
		coin_value = get_coin_balance(coin)
		usd_price, rub_price, btc_price = get_coin_price(coin)
		usd_value = usd_price * coin_value
		rub_value = rub_price * coin_value
		btc_value = btc_price * coin_value
		total['USD'] += usd_value
		total['RUB'] += rub_value
		total['BTC'] += btc_value
		coin_value = "{0:.4f}".format(coin_value)
		usd_value = "{0:.4f}".format(usd_value)
		rub_value = "{0:.4f}".format(rub_value)
		btc_value = "{0:.4f}".format(btc_value)		
		coin_balance = [coin, coin_value, usd_value, rub_value, btc_value]
		balance.append(coin_balance)
	return render_template('balance.html', balance=balance, total=total)


@app.route('/log.html')
def log():
	return render_template('log.html')


def get_current_coin():
	with open(COIN, 'r') as f:
		return f.read()


def get_process_name():
	lines = open(PID).readlines()
	return [line.strip() for line in lines if line != '\n']


def get_pid_by_name(process_name):
	for process in psutil.process_iter():
		if process_name.lower() == process.name().lower():
			return process.pid


def get_process_uptime(process_name):
	for process in psutil.process_iter():
		if process_name[0].lower() == process.name().lower():
			create_time = process.create_time()
			now = time()
			diff = int(now - create_time)
			m, s = divmod(diff,60)
			h, m = divmod(m,60)
			return "%02d:%02d:%02d" %(h,m,s)
	print "Process %s not found" %process_name[0]


def get_coin_balance(coin):
	with open(BALANCE) as f:
		reader = csv.reader(f)
		value = dict()
		for row in reader:
			if row[0] == coin:
				return float(row[1])


def get_market_prices():
	API = "https://min-api.cryptocompare.com/data/pricemulti"
	MY_COINS = 'BTC,ETH,ETC,ZEC,XVG,ZCL,XMR,KMD,HUSH'
	MY_CUR = 'USD,RUB,BTC'
	payload = {'fsyms': MY_COINS, 'tsyms': MY_CUR}
	req = requests.get(API, params=payload)
	r = req.json()
	rez = []
	for k,v in r.iteritems():
		rez.append([k, v['USD'], v['RUB'], v['BTC']])
	return sorted(rez, key=itemgetter(0))


def get_coin_price(coin):
	prices = get_market_prices()
	for price in prices:
		if coin == price[0]:
			return price[1], price[2], price[3]


class BalanceData(object):
	def __init__(self, interval=3600):
		self.interval = interval
		self.COINS = ['ZEC','BTC','ETH','XVG']
		self.API = os.path.join(WORK_DIR, 'api.conf')
		self.BALANCE = os.path.join(WORK_DIR, 'balance.csv')
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                         
		thread.start()
	def run(self):
		requests.packages.urllib3.disable_warnings()
		cfg = SafeConfigParser()
		cfg.read(self.API)
		while True:
			with open(self.BALANCE) as f:
				lines = list(csv.reader(f))
			for coin in self.COINS:
				url = cfg.get(coin, 'BALANCE')
				req = requests.get(url, verify=False)
				if coin == "BTC":
					value = float(req.json())/10**8
				elif coin == 'ZEC':
					value = float(req.json()['balance'])
				elif coin in ["ETH", "ETC"]:
					value = float(req.json()['balance'])/10**18
				elif coin == 'XVG':
					value = float(req.json())		
			for line in lines:
				if line[0] == coin:
					line[1] = value
			with open(BALANCE, 'wb') as f:
				writer = csv.writer(f)
				writer.writerows(lines)
			sleep(self.interval)

		


'''
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

'''





if __name__ == "__main__":
	BalanceData()
	app.run(host="0.0.0.0", debug = True)




