from datetime import datetime, timezone, timedelta
from json import dumps

from pymongo import MongoClient

client = MongoClient("mongodb+srv://ConnectionCred:D5ONW4P5kHLtjErK@cluster0.52i7u.mongodb.net/analytics?retryWrites=true&w=majority")

entrys = client.analytics.entrys
processed = client.analytics.processed 

def comb_dicts(list_of_dict):
	return_dict = {}
	for x in list_of_dict:
		return_dict.update(x)
	
	return return_dict


def get_epoch_for_date(date_string):
	"""
	The `date_string` must be in the format "yyyy-mm-dd"

	The date string will be converted into a start and end epoch for the day 
	and then query the database and parse the responses
	"""

	datetime_string_split = [int(x) for x in date_string.split('-')]
	start = datetime(datetime_string_split[0], datetime_string_split[1], datetime_string_split[2], tzinfo=timezone.utc)
	end = start + timedelta(1)

	start_epoch, end_epoch = start.timestamp(), end.timestamp()

	return start_epoch, end_epoch


def get_epoch_for_datehour(datetime_string):
	"""
	The `date_string` must be in the format "yyyy-mm-dd-hr"

	The date string will be converted into a start and end epoch for the day 
	and then query the database and parse the responses
	"""

	datetime_string_split = [int(x) for x in datetime_string.split('-')]
	start = datetime(datetime_string_split[0], datetime_string_split[1], datetime_string_split[2], datetime_string_split[3], tzinfo=timezone.utc)
	end = start + timedelta(hours=1)

	start_epoch, end_epoch = start.timestamp(), end.timestamp()

	return start_epoch, end_epoch

def query(start_epoch, end_epoch, subobject, what_to_query):
	if what_to_query == "pageview":
		return list(entrys.aggregate([
			{"$match": {"date_epoch": {"$gte": start_epoch, 
										"$lt": end_epoch}}},
			{"$group": {"_id": "$"+subobject,
						"count": {"$sum": 1}}},
			{"$sort": {"count": -1}},

			# the next 3 lines convert the aggregation from [{"value": "firefox", "count": 40}, {"value": "chrome", "count": 2}]
			# to this [{"firefox": 40, "chrome": 2}]
			{"$group": {"_id": None, "results": {"$push": {"k": "$_id", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))[0]
	elif what_to_query == "session":
		return list(entrys.aggregate([
			{"$match": {"date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
    		{ "$group": { "_id": "$"+subobject, "values": { "$addToSet": "$sess_id" } } },
			{ "$project": { "_id": 0, "value": "$_id", "count": { "$size": "$values" } } },
			{"$sort": {"count": -1}},

			# the next 3 lines convert the aggregation from [{"value": "firefox", "count": 40}, {"value": "chrome", "count": 2}]
			# to this [{"firefox": 40, "chrome": 2}]
			{"$group": {"_id": None, "results": {"$push": {"k": "$value", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))[0]
	elif what_to_query == "unique_visits":
		return list(entrys.aggregate([
			{"$match": {"date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
    		{ "$group": { "_id": "$"+subobject, "values": { "$addToSet": "$v_id" } } },
			{ "$project": { "_id": 0, "value": "$_id", "count": { "$size": "$values" } } },
			{"$sort": {"count": -1}},

			# the next 3 lines convert the aggregation from [{"value": "firefox", "count": 40}, {"value": "chrome", "count": 2}]
			# to this [{"firefox": 40, "chrome": 2}]
			{"$group": {"_id": None, "results": {"$push": {"k": "$value", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))[0]
	elif what_to_query == "path_count":
		return list(entrys.aggregate([
			{"$match": {"date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
    		{ "$group": { "_id": "$path", "values": { "$push": "$path" } } },
			{ "$project": { "_id": 0, "value": "$_id", "count": { "$size": "$values" } } },
			{"$sort": {"count": -1}},

			# the next 3 lines convert the aggregation from [{"value": "firefox", "count": 40}, {"value": "chrome", "count": 2}]
			# to this [{"firefox": 40, "chrome": 2}]
			{"$group": {"_id": None, "results": {"$push": {"k": "$value", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))
	elif what_to_query == "new_sess":
		return list(entrys.aggregate([
			{"$match": {"new_sess": True,
			            "date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
			{"$group": {"_id": "$"+subobject,
			            "count": {"$sum": 1}}},
			{"$sort": {"count": -1}},


			{"$group": {"_id": None, "results": {"$push": {"k": "$_id", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))[0]
	elif what_to_query == "new_visit":
		return list(entrys.aggregate([
			{"$match": {"new_visit": True,
			            "date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
			{"$group": {"_id": "$"+subobject,
			            "count": {"$sum": 1}}},
			{"$sort": {"count": -1}},


			{"$group": {"_id": None, "results": {"$push": {"k": "$_id", "v": "$count"}}}},
			{"$project": {"_id": 0,	"res": {"$arrayToObject": "$results"}}},
			{"$replaceRoot": {"newRoot": "$res"}}
		]))[0] 
	elif what_to_query == "count_x":
		return list(entrys.aggregate([
			{"$match": {"date_epoch": {"$gte": start_epoch, 
			                           "$lt": end_epoch}}},
			{ "$group": { "_id": None, "ids": { "$addToSet": "$"+subobject } } }, 
			{ "$project": { "value": { "$size": "$ids" } } }
		]))

	


def combine_aggregations(data_object):
	"""
		data_object must return a list of dicts or must be a iterable object (for example a generator)
		with the name of the the type of data for example "Session" or "Visitors"
		and a dict with the url data for example
		
		[{
			"type": "Session"
			"data": {
				"/ajaja": 13
			}
		}]

		it can also contain multiple urls for example
		[{
			"type": "Session"
			"data": {
				"/ajaja": 13,
				"/data": 94,
				"/aiuw/irs/aoijdwoa": 9032,
				"/aaa/aaa/aaa": 40932
			}
		}]
	"""

	types = set()
	for data in data_object:
		types.add(data['type'])


	return_dict = {}

	for z in data_object:
		for x, y in z['data'].items():
			if x not in return_dict:
				return_dict[x] = {}
				for v in types:
					return_dict[x][v] = 0

			#w = return_dict[x]
			return_dict[x][z['type']] = y
			#return_dict[x] = w
	
	return return_dict

"""print(combine_url_data(	[{
		"type": "Session",
		"data": {
			"/ajaja": 13,
			"/data": 94,
			"/aiuw/irs/aoijdwoa": 9032,
			"/aaa/aaa/aaa": 40932
		}
	},
	{
		"type": "Pageviews",
		"data": {
			"/ajaja": 1,
			"/data": 75,
			"/aiuw/irs/aoijdwoa": 33,
			"/aaa/aaa/aaa": 7
		}
	}]))
"""

def query_and_process(start_epoch, end_epoch, datetime_string):
	return {
		"time_str": datetime_string,
		"start_epoch": start_epoch, 
		"end_epoch": end_epoch,
		"ua": {
			"browser": {
				"pageview": query(start_epoch, end_epoch, "ua.br", "pageview"),
				"session": query(start_epoch, end_epoch, "ua.br", "session"),
				"visitors": query(start_epoch, end_epoch, "ua.br", "new_visit")
			},
			"device": {
				"pageview": query(start_epoch, end_epoch, "ua.dv", "pageview"),
				"session": query(start_epoch, end_epoch, "ua.dv", "session"),
				"visitors": query(start_epoch, end_epoch, "ua.dv", "new_visit")
			},
			"os": {
				"pageview": query(start_epoch, end_epoch, "ua.os", "pageview"),
				"session": query(start_epoch, end_epoch, "ua.os", "session"),
				"visitors": query(start_epoch, end_epoch, "ua.os", "new_visit")
			}
		},
		"urls": combine_aggregations([
			{"type": "page_view", "data": query(start_epoch, end_epoch, "path", "pageview")},
			{"type": "unique_page_view", "data": query(start_epoch, end_epoch, "path", "session")},
			{"type": "new_visit", "data": query(start_epoch, end_epoch, "path", "new_visit")},
			{"type": "page_enter", "data": query(start_epoch, end_epoch, "path", "new_sess")},
			{"type": "unique_users", "data": query(start_epoch, end_epoch, "path", "unique_visits")}
		]),
		"country": combine_aggregations([
			{"type": "page_view", "data": query(start_epoch, end_epoch, "ip.contryCode", "pageview")},
			{"type": "sessions", "data": query(start_epoch, end_epoch, "ip.contryCode", "new_sess")},
			{"type": "visitors", "data": query(start_epoch, end_epoch, "ip.contryCode", "new_visit")},
		]),
	}


#print(run_all_needed_querys_between(1800, processed_entry_length="hour", starttime=int(datetime(2020, 8, 5, 1).timestamp()), endtime=1597421100))

if __name__ == "__main__":
	date = "2020-07-24"
	start, end = get_epoch_for_date(date)
	print(dumps(query_and_process(0, 10000000000000000, date)))