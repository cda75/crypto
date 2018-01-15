import requests
from time import sleep



API_URL = "https://min-api.cryptocompare.com/data/price?"
CRYPTO = ["BTC", "XMR", "ZEC", "ZCL", "ETH", "XRP", "XVG"]
CUR = "RUB"


def get_all_crypto():
	for crypto in CRYPTO:
		payload = {'fsym': crypto, 'tsyms': CUR}
		req = requests.get(API_URL, params=payload)
		result = req.json()[CUR] 
		print "%s: %s %s" %(crypto, result, CUR)


def get_price(crypto, cur):
	payload = {'fsym': crypto, 'tsyms': CUR}
	req = requests.get(API_URL, params=payload)
	result = req.json()[CUR]
	print "%s: %s %s" %(crypto, result, CUR)
	return result


if __name__ == "__main__":
	while True:
		get_all_crypto()
		print "\n---------------------------------------\n"
		sleep(60)

