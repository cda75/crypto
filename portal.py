# -*- coding: utf-8 -*-

import requests
from time import sleep
import os
from ConfigParser import SafeConfigParser 
import json
#import pandas as pd
from flask import Flask
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime



API_URL = "https://min-api.cryptocompare.com/data/price?"
WORK_DIR = os.path.dirname(os.path.realpath(__file__))
COINS = os.path.join(WORK_DIR, 'coins.conf')
API = os.path.join(WORK_DIR, 'api.conf')

#API DOC at "https://github.com/MPOS/php-mpos/wiki/API-Reference"
#MPH_API = "https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]"

cfg = SafeConfigParser()
cfg.read(COINS)
MY_COINS = cfg.sections()


def get_price(coin, cur='USD'):
	payload = {'fsym': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	return req.json()[cur]

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
	elif coin == 'ZCL':
		url = cfg.get(coin, 'API_URL')
		api_key = cfg.get(coin, 'API_KEY')
		arg = cfg.get(coin, 'USER_ID')
		payload = {'page': 'api', 'action': 'getusertransactions', 'api_key': api_key, 'argument': arg}
		req = requests.get(url, params=payload)
		value = 0
		tx = req.json()['getusertransactions']['data']['transactions']
		for i in tx:
			if 'Debit' in i['type']:
				print i['amount'], i['timestamp']
				value +=i['amount']


	return value







if __name__ == "__main__":
	print get_balance('ZCL')



