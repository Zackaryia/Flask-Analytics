from json import dump, load

custom_geo_obj = {}
mini_geo = {"type":"FeatureCollection","features":[]}
with open('/home/z/Desktop/Flask-Boiler-Plate/blueprints/analytics/static/js/countrys.json') as custom_geo:
	custom_geo_obj = load(custom_geo)

import math
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

for country in custom_geo_obj['features']:
	mini_country = {
		"type":"Feature",
		"properties":{"name": country['properties']['name'],"iso_a2": country['properties']['iso_a2']},
		"geometry":{"type":"MultiPolygon","coordinates":[]}
	}


	if isinstance(country['geometry']['coordinates'][0][0][0], (int, float)):
		is_int = True
	else:
		is_int = False
	
	if country['geometry']['type'] == "MultiPolygon":
		mini_country['geometry']['type'] = "MultiPolygon"
		for polygon_count, polygon in enumerate(country['geometry']['coordinates']):
			mini_country['geometry']['coordinates'].append([])
			for polygon_part_count, polygon_part in enumerate(polygon):
				mini_country['geometry']['coordinates'][polygon_count].append([])
				for polygon_part_point_count, polygon_part_point in enumerate(polygon_part):
					mini_country['geometry']['coordinates'][polygon_count][polygon_part_count].append([])
					for cord_count, cord in enumerate(polygon_part_point):
						mini_country['geometry']['coordinates'][polygon_count][polygon_part_count][polygon_part_point_count].append(truncate(cord, 5))
					#mini_country['geometry']['coordinates'][polygon_count][polygon_part_count].append([])
	else:
		mini_country['geometry']['type'] = "Polygon"
		for polygon_part_count, polygon_part in enumerate(country['geometry']['coordinates']):
			mini_country['geometry']['coordinates'].append([])
			for polygon_part_point_count, polygon_part_point in enumerate(polygon_part):
				mini_country['geometry']['coordinates'][polygon_part_count].append([])
				for cord_count, cord in enumerate(polygon_part_point):
					mini_country['geometry']['coordinates'][polygon_part_count][polygon_part_point_count].append(truncate(cord, 4))

	
	mini_geo['features'].append(mini_country)

	#mini_geo.append('')

with open('/home/z/Desktop/Flask-Boiler-Plate/blueprints/analytics/static/js/minified_countrys.json', 'w+') as minified:
	dump(mini_geo, minified, separators=(',', ':'))
