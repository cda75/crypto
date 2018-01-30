# -*- coding: utf-8 -*-

import requests
from time import sleep
import os
from ConfigParser import SafeConfigParser 
import json
import pandas as pd
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
import csv
from operator import itemgetter



API_URL = "https://min-api.cryptocompare.com/data/pricemulti"
WORK_DIR = os.path.dirname(os.path.realpath(__file__))
COINS = os.path.join(WORK_DIR, 'coins.conf')
API = os.path.join(WORK_DIR, 'api.conf')
PRICE = os.path.join(WORK_DIR, 'price.csv')

#API DOC at "https://github.com/MPOS/php-mpos/wiki/API-Reference"
#MPH_API = "https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]"


MY_COINS = 'BTC,ETH,ETC,ZEC,ZCL,XMR,XVG,KMD,HUSH'


def get_price(coin=MY_COINS, cur='USD,RUB,BTC'):
	payload = {'fsyms': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	r = req.json()
	rez = []
	for k,v in r.iteritems():
		rez.append([k,v['USD'],v['RUB'],v['BTC']])
	return sorted(rez, key=itemgetter(0))


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



def write_prices_csv():
	prices = get_price()
	header = ['COIN','USD','RUB','BTC']
	with open(PRICE, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(header)
		for row in prices:
			writer.writerow(row)


def make_dash_table(df):
	table = []
	for index, row in df.iterrows():
		html_row = []
		for i in range(len(row)):
			html_row.append(html.Td([row[i]]))
		table.append(html.Tr(html_row))
	return table


df_prices = pd.read_csv(PRICE)


def main():
	colors = {'background': '#111111', 'text1': '#7FDBFF', 'text2': '#FFFFFF'}
	app = dash.Dash()
	#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
	app.layout = 	html.Div(	style={'backgroundColor': colors['background']},
							children=[
								html.H1('Mining Portal', style={'textAlign': 'center', 'color': colors['text1']}),
								html.Div('Monitoring workers, coins, and more...', style={'textAlign': 'center', 'color': colors['text1']}),
								html.Br([]),
								html.Div([html.H2('Market Prices', className="gs-header gs-text-header padded", style={'color': colors['text2']} ),
										html.Table(make_dash_table(df_prices), className='blue-text', style={'color': colors['text2']})
										], className="four columns")
								]
							)
	

	app.run_server(debug=True)

if __name__ == "__main__":
	main()



