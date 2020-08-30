from json import dumps
from util.json_dumps import json_serial

def session_to_dict(session, return_dict=False, return_html=True):
	session_values = list(session.values())
	session_keys   = list(session.keys())

	session_dict   = {}


	for x in range(len(session_keys)):
		session_dict[session_keys[x]] = session_values[x]

	if return_dict:
		return session_dict
	else:
		if return_html:
			return dumps(session_dict, indent=4, default=json_serial).replace('    ', '&emsp;&emsp;').replace('\n', '<br>')
		else:
			return dumps(session_dict, indent=4, default=json_serial) 