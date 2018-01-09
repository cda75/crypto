import requests



API_URL = "https://min-api.cryptocompare.com/data/price?"
CRYPTO = ["BTC", "XMR", "ZEC", "ETH", "XRP", "XVG"]
CUR = "USD"


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
	get_all_crypto()

