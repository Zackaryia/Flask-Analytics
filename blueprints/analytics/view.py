from flask import Blueprint, render_template, current_app, g, make_response, request, session, jsonify, ctx, url_for
from blueprints.analytics.ip_to_geo import get_ip
from blueprints.analytics.analytics_parse import query_and_process, query

from util.insert_into_head import insert_script_into_head
from util.parse_referrer import parse_referrer_for_url
from util.json_dumps import json_serial
from util.gen_string import gen_string
from util.parse_ua import ua_parse


from pymongo import MongoClient, ASCENDING, DESCENDING
from itsdangerous import URLSafeSerializer
from bson import ObjectId


from datetime import datetime, timezone
from user_agents import parse
from time import sleep
from json import dumps, loads


analytics = Blueprint('analytics', __name__, template_folder='templates', static_folder='static', static_url_path='static')



with open('blueprints/analytics/country_2_alpha.json', 'r') as countries_file:
	countries_json = loads(countries_file.read())


funcs_to_include = []
funcs_to_exclude = []

def include(self):
	funcs_to_include.append(self)


def exclude(self):
	funcs_to_exclude.append(self)


def determin_run_anal(endpoint): # Weather or not to run the analytics. 
	print(endpoint)
	if endpoint == None:
		return app.config.get('ANALYTICS_DEFAULT_RUN')

	


	if endpoint == "static" or (len(endpoint.split('.')) > 1 and endpoint.split('.')[1] == "static"):
		return app.config.get('ANALYTICS_LOG_STATIC')


	function = app.view_functions[endpoint]

	if function in funcs_to_include:
		return True
	elif function in funcs_to_exclude:
		return False
	else: #If the function is in nither the include or exclude functions it
		#will detetmin weather or not to run if it is defaulted to run
		return app.config.get('ANALYTICS_DEFAULT_RUN')

"""

funcs_to_include_js_analytics = []
funcs_to_exclude_js_analytics = []

def include_js_analytics(self):
	funcs_to_include_js_analytics.append(self)


def exclude_js_analytics(self):
	funcs_to_exclude_js_analytics.append(self)

def determin_run_js_anal(endpoint): # Whether or not to run the js analytics.
	if endpoint == None:
		return False

	function = app.view_functions[endpoint]

	if function in funcs_to_include_js_analytics:
		return True
	elif function in funcs_to_exclude_js_analytics:
		return False
	else: #If the function is in nither the include or exclude it
		#will detetmin wether or not to run if it is defaulted to run
		return app.config.get('ANALYTICS_JS_DEFAULT_RUN')
"""




@analytics.before_app_request
def before_request_log():

	#Logs what time the begining of the request is
	current_epoch = datetime.now().timestamp()

	g.start_request_time = current_epoch
	g.tracked_vars = {}


js_analytics_min = """
"""

@analytics.after_app_request
def after_request_log(response):    
	"""
	Does most of the heavy lifting in the logging and is the spine of other
	functions to process data
	
	TODO log the users useragent and respect DNT headers (do not track)
	"""

	if determin_run_anal(request.endpoint):

		# TODO
		# in the future add javascript tracking as well to know when a user actually leaves a page and other info in the same vein
		# also it would add the ability to log special events such as button clicks and image views

		# if response.mimetype == 'text/html' and determin_run_js_anal(request.endpoint):
		# 	response.data = insert_script_into_head(response.data, f"""
		# 	function log_event(n){{$.post("{url_for("analytics.analytics_post")}",{{event:n}})}};
		# 	window.addEventListener("beforeunload",function(n){{log_event("{post_request_signer.dumps("pageUnload:"+gen_string(6))}")}});
		# 	""")

		if request.headers.get('Dnt') == 1:
			dnt_disallow = True

		#if g.log and (not dnt_disallow) or g.force_log

		new_visitor = False
		
		if "v_id" in session:
			g.v_id = session['v_id']
		else:
			new_visitor = True
			v_id = gen_string(16)
			g.v_id = v_id
			session['v_id'] = v_id
		
		
		
		#"sess_id" in session and "sess_id_use" in session
		if all(x in session for x in ['sess_id', 'sess_id_use']) and g.start_request_time-session['sess_id_use'] < app.config.get('ANALYTICS_SESSION_LENGTH_SEC'):
			g.sess_id = session['sess_id']
			session['sess_id_use'] = g.start_request_time
			new_session = False
		else: # if there is no session id, no session id use timestamp, or a expired session id then it will make a new one		
			new_session = True
			sess_id = gen_string(20)
			g.sess_id = sess_id
			session['sess_id'] = sess_id
			session['sess_id_use'] = g.start_request_time

		
		referrer_domestic = None

		if request.referrer:
			referrer_domestic = session['ref_url']


		ip_info = get_ip(request.remote_addr)

		if parse_referrer_for_url(request.referrer) == request.host:
			referrer_domestic = request.referrer
		
		parsed_ua = parse(request.user_agent.string)

		request_dict = {
			"_id": ObjectId(),

			"ip": ip_info,
			"ua": {
				"br": parsed_ua.browser[0][:30], 
				"os": parsed_ua.os[0][:30], 
				"dv": parsed_ua.device[0][:30], 
				"is": {
					"mobile": parsed_ua.is_mobile,
					"tablet": parsed_ua.is_tablet,
					"touch":  parsed_ua.is_touch_capable,
					"pc":     parsed_ua.is_pc,
					"bot":    parsed_ua.is_bot 
				}
			},

			"status": response.status_code,
			"response_len": response.content_length,
			"method": request.method,


			"referrer": request.referrer,
			"referrer_domestic": referrer_domestic,
			"referrer_host": parse_referrer_for_url(request.referrer),

			"path": request.path,
			"url_args": request.full_path[len(request.path):],
			"endpoint": request.endpoint,


			"date": datetime.fromtimestamp(g.start_request_time, tz=timezone.utc),
			"date_epoch": g.start_request_time,
			"sess_id": g.sess_id,
			"v_id": g.v_id,
			"new_visit": new_visitor,
			"new_sess": new_session,

			"tracked_var": g.tracked_vars,
			"time_to_respond": (datetime.now().timestamp() - g.start_request_time),
			"event": "pageLoad"
		}

		print(dumps(request_dict, default=json_serial))

		analytics_mongo.insert_one(request_dict)

		session['ref_url'] = request.url


	return response

@exclude
@analytics.route('/post', methods=['POST'])
def analytics_post():
	return jsonify(request.form.to_dict())



@analytics.route('/example/<test>')
def example_test(test):
	return render_template('main.html', example=test)


@analytics.route('/post_ajax')
def post_ajax():
	return render_template('test_ajax_post.html')

@analytics.route('/example')
def example():
	return str(current_app.view_functions['static'])

@analytics.route('/dashboard')
def dashboard():
	date = "2020-07-24"
	query_data = query_and_process(0, 10000000000000000, date)
	print(query_data)
	entrys_10 = list(analytics_mongo.find({}, limit=20).sort("date_epoch", DESCENDING))
	return render_template('analytics.html', entrys=entrys_10)

@analytics.route('/dashboard/geo')
def dashboard_geo(): 
	date = "2020-07-24"
	query_data = query_and_process(0, 10000000000000000, date)
	for x, y in query_data['country'].items():
		if x in countries_json.keys():
			y['name'] = countries_json[x]
		else:
			y['name'] = "Unknown"
	print(query_data )
	return render_template('analytics_geo.html', query_data=query_data)

@analytics.route('/dashboard/live')
def dashboard_live():


	return render_template('analytics_live.html')

@exclude
@analytics.route('/dashboard/live/data', methods=['POST', 'GET'])
def dashboard_live_data():
	sess_len = app.config.get('ANALYTICS_SESSION_LENGTH_SEC')
	epoch = int(datetime.now().timestamp())
	start_epoch = int(epoch)-sess_len

	y = query(start_epoch, epoch, "sess_id", "count_x") 


	if len(y) > 0:
		value = y[0]['value']
	else:
		value = 0
	return {"value": str(value), "paths": query(start_epoch, epoch, "", 'path_count')}

	
@analytics.record_once
def load_config(setup_state):
	global app 

	app = setup_state.app	

	client = MongoClient(app.config.get('MONGO_URI_ANALYTICS'))


	global analytics_mongo
	analytics_mongo = client.analytics.entrys 


	# the javascript tracker event encryptor so users can not forge events
	# this is turned off until the javascript tracker is built

	# global post_request_signer
	# post_request_signer = URLSafeSerializer(secret_key=app.config.get('SECRET_KEY'), salt='post request signer')