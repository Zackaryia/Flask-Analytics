from user_agents import parse
from json import dumps

def ua_parse(user_agent_string):
	parsed = parse(user_agent_string)
	print(dumps(parsed))
	return {
		"mobile": parsed.is_mobile,
		"tablet": parsed.is_tablet,
		"touch":  parsed.is_touch_capable,
		"pc":     parsed.is_pc,
		"bot":    parsed.is_bot 
	} 