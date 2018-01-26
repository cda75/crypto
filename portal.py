import requests
from time import sleep
import os
from ConfigParser import SafeConfigParser 



API_URL = "https://min-api.cryptocompare.com/data/price?"
WORK_DIR = os.path.dirname(os.path.realpath(__file__))
COINS = os.path.join(WORK_DIR, 'coins.conf')


cfg = SafeConfigParser()
cfg.read(COINS)
MY_COINS = cfg.sections()


def get_price(coin, cur='USD'):
	payload = {'fsym': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	return req.json()[cur]

def get_balance(coin):
	cfg = SafeConfigParser()
	cfg.read(COINS)
	api = cfg.get(coin, 'API')
	req = requests.get(api)
	if coin == "BTC":
		value = float(req.json())/10**8
	elif coin == "ZEC":
		value = float(req.json()['balance'])
	elif coin == 'XVG':
		value = float(req.json())
	return value



if __name__ == "__main__":
	p = get_balance('XVG')
	print p


