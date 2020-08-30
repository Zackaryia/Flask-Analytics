from urllib.request import urlopen
from json import loads, dumps, load
from datetime import datetime, timedelta
from cachetools import cached, TTLCache, LRUCache
from socket import gethostbyaddr
from json import load

with open('keys.json') as keysFile:
	config = load(keysFile)


#to add more functions to process ip's add this line and replace function for the function name
#The function must return in the same format as ipwhois and ipgeolocation

#config['order_funcs'].append(Function)




last_time_torlist_downloaded = datetime(1970, 1, 1)
tor_ip_list = []


def reset_time_torlist_downloaded():
	global last_time_torlist_downloaded
	last_time_torlist_downloaded = datetime.now()

#print(urlopen('https://extreme-ip-lookup.com/csv/63.70.164.200').read())

@cached(TTLCache(maxsize=2048, ttl=30*60))
def is_tor_exit_point(ip):
	"""
	Checks if an ip is the same of a tor exit node by checking the tor projects website
	"""
	time_delta = datetime.now() - last_time_torlist_downloaded

	if time_delta > timedelta(minutes=10):
		reset_time_torlist_downloaded()
		response = urlopen("https://check.torproject.org/torbulkexitlist").read()

		global tor_ip_list
		tor_ip_list = response.splitlines()

	if ip in tor_ip_list:
		return True
	else:
		return False



@cached(TTLCache(maxsize=2048, ttl=30*60))
def get_ip(ip):
	"""
	gets the info for the ip and calls the functions ipwhois and ipgeolocation to get the info for the ip and if both
	functions are not able to get the users ip info it will default to the config keys.order_funcs functions to get
	function to call to get the users ip info
	"""
	order_funcs = config['order_funcs']

	if ip == "127.0.0.1": #if the ip is localhost
		return {
			'ip': ip,
			'host': "localhost",
			"city": "?null?",
			"region": "?null?",
			"contryCode": "??",
			"continentCode": "??",
			"lon": None,
			'lat': None,

			'asn': 'AS0',
			'org': '?none?',
			'isp': "?none?",

			'is_tor': False
		}


	for func in order_funcs:
		if func == "ipwhois":
			return_value = ipwhois(ip)
			if return_value != False: # if there are no errors then return the value from ipwhois
				return return_value
		elif func == "ipgeolocation":
			return_value = ipgeolocation(ip, config['IPGEOKEY'])
			if return_value != False: # if there are no errors then return the value from ipgeolocation
				return return_value
		elif type(func) != str:
			return_value = func
			if return_value != False: # if there are no errors then return the value from func
				return return_value

	try:
		host = gethostbyaddr(ip)[0]
	except:
		host = None

	try:
		net = IPWhois(ip)
		asn = net.lookup_whois()['asn']
	except:
		asn = None

	# if no function is able to run without errors then it will just return the info that does not need any 3rd party libs
	return {
		'ip': ip,
		'host': host,

		'asn': asn,

		'is_tor': is_tor_exit_point(ip)

	}




@cached(TTLCache(maxsize=2048, ttl=30*60))
def ipwhois(ip):
	try:
		response = urlopen("http://ipwhois.app/json/" + ip + "?objects=city,region,country_code,continent_code,longitude,latitude,asn,org,isp")
		ip_json_dict = load(response)

		try:
			host = gethostbyaddr(ip)
		except:
			host = None

		return_dict = {
			'ip': ip,
			'host': host,

			'city': ip_json_dict['city'],
			'region': ip_json_dict['region'],
			'contryCode': ip_json_dict['country_code'],
			'continentCode': ip_json_dict['continent_code'],

			'lon': float(ip_json_dict['longitude']),
			'lat': float(ip_json_dict['latitude']),

			'asn': ip_json_dict['asn'],
			'org': ip_json_dict['org'],
			'isp': ip_json_dict['isp'],

			'is_tor': is_tor_exit_point(ip)
		}

		return return_dict

	except:
		return False



@cached(TTLCache(maxsize=2048, ttl=30*60))
def ipgeolocation(ip, apikey):
	try:
		response = urlopen(f"https://api.ipgeolocation.io/ipgeo?apiKey={apikey}&ip={ip}&output=json")
		ip_json_dict = load(response)

		net = IPWhois(ip)
		asn = net.lookup_whois()['asn']

		try:
			host = gethostbyaddr(ip)
		except:
			host = None

		return_dict = {
			'ip': ip,
			'host': host,

			'city': ip_json_dict['city'],
			'region': ip_json_dict['state_prov'],
			'contryCode': ip_json_dict['country_code2'],
			'continentCode': ip_json_dict['continent_code'],

			'lon': float(ip_json_dict['longitude']),
			'lat': float(ip_json_dict['latitude']),

			'asn': asn,
			'org': ip_json_dict['organization'],
			'isp': ip_json_dict['isp'],

			'is_tor': is_tor_exit_point(ip)
		}

		return return_dict

	except:
		return False
