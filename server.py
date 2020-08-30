from flask import Flask, request, jsonify, g, make_response, session, render_template, url_for, redirect
from flask_compress import Compress

from util.saferproxy import SaferProxyFix
from util.session_to_dic import session_to_dict

from blueprints.analytics import analytics, include, exclude

from json import dumps

app = Flask(__name__, static_folder="static", static_url_path='/s')
Compress(app)

app.wsgi_app = SaferProxyFix(app.wsgi_app)
#app.config['SERVER_NAME'] = 'localhost:80'
app.config.from_json('keys.json')

@exclude
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))




app.register_blueprint(analytics, url_prefix="/analytics")



@app.route('/')
def home():
	print(request.args)
	return make_response(render_template("main.html", example=request.referrer))

@app.route('/session')
def session_return():
	if app.config['DEBUG']:
		return jsonify(session_to_dict(session, return_dict=True))
	else:
		return "Session"


@app.route('/g')
def g_return():
	if app.config['DEBUG']:
		return jsonify(g.__dict__) 
	else:
		return "G"

@app.route('/ip')
def aaa():
	y = dumps(request.headers)
	return y


if __name__ == "__main__":
	app.run(debug=True)	
