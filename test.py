def overclock_running():
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	oc_prog = os.path.basename(cfg.get('OVERCLOCK','PATH'))
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == oc_prog:
			return True
	return False


def start_overclock(profile=1):
	cfg = SafeConfigParser()
	cfg.read(CONFIG_FILE)
	oc_prog = os.path.abspath(cfg.get('OVERCLOCK','PATH'))
	cmdStr = "%s \s -Profile%s" %(oc_prog, profile)
	Popen(cmdStr)
	sleep(5)


def get_ZEC_profit(hashrate):
	FLYPOOL_API_URL = "https://api-zcash.flypool.org/poolStats"
	req = requests.get(FLYPOOL_API_URL)
	data = req.json()['data']
	PF = 0.99
	NH = data['poolStats']['hashRate']
	BpH = data['poolStats']['blocksPerHour']
	profit = get_coin_profit('ZEC', hashrate, NH, BpH)
	return profit


def get_XVG_profit(hashrate):
	API_URL = "http://xvg-lyra.idcray.com/index.php?"
	payload = {'page': 'api', 'action':'getpoolstatus', 'api_key': 'e427e3be81c79df098d074e351902bb1b210574a4fd6d641f42b74a0baafb7df'}
	req = requests.get(API_URL, params=payload)
	data = req.json()[payload['action']]['data']
	NH = data["hashrate"]
	BpH = 3600/data['esttime']
	profit = get_coin_profit('XVG', hashrate, NH, BpH)
	return profit


def get_ZCL_profit(hashrate):
	API_URL = "https://zclassic.miningpoolhub.com/"
	payload = {'page': 'api', 'action':'getpoolstatus', 'api_key': 'cfdbe7a47bcdcb088d0e11aee243679963c1806f74861136c2b7043a6a89e4a5'}
	req = requests.get(API_URL, params=payload)
	data = req.json()[payload['action']]['data']
	NH = data["hashrate"]
	BpH = 3600/data['esttime']
	profit = get_coin_profit('ZCL', hashrate, NH, BpH)
	return profit


def get_coin_profit(coin, HR, NH, BpH):
	BR = get_coin_data(coin)[0]
	P = get_coin_price(coin,'usd')
	usd_profit = HR*BpH*BR*P/NH
	coin_profit = HR*BpH*BR/NH
	return 24*usd_profit, 24*coin_profit


def get_coin_price(coin, cur):
	cur = cur.upper()
	coin = coin.upper()
	API_URL = "https://min-api.cryptocompare.com/data/price?"
	payload = {'fsym': coin, 'tsyms': cur}
	req = requests.get(API_URL, params=payload)
	result = req.json()[cur] 
	return result


def get_coin_data(coin):
	coin = coin.upper()
	URL = "http://whattomine.com/coins.json"
	req = requests.get(URL)
	data = req.json()['coins'].values() 
	for v in data:
		if v["tag"] == coin:
			block_reward = v["block_reward"]
			block_time = float(v["block_time"])
			algo = v["algorithm"]
			profit = v["profitability"]
			nethash = v["nethash"]
			diff = v["difficulty"]
	return block_reward, block_time, profit

