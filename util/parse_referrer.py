from werkzeug.urls import url_parse
from re import fullmatch


def parse_referrer_for_url(referrer):
	if referrer == None or referrer == "None" or type(referrer) == None:
		return None
	elif type(fullmatch('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', referrer)) != None:
		return url_parse(referrer).host
	else:
		return referrer