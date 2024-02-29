import shapely.geometry as sg
from fiona import open as fio
import json, os
import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout.buffer)
os.environ["PROJ_LIB"] = r"D:\Programs\QGIS 3.28.3\share\proj"

with open(r"C:\Users\TK4\Desktop\out.json", encoding='utf-8') as f:
	j = json.load(f)

features = []
schema = []
spatial_ref = j['crs']['properties']['name']


item = j["features"][0]
attribute = item["properties"]
coordinates = item['geometry']['coordinates']

for feature in attribute:
	if type(feature) == str:
		schema.append((feature, 'str'))
	elif type(feature) == int:
		schema.append((feature, 'int'))
	else:
		schema.append((feature, 'str'))

schema = set(schema)
schema = list(schema)
schema = {
	'geometry': 'Point',
	'properties': schema
}

# if len(schema['properties']) != len(features[0]['properties']):
# 	print("Schema Error")
# 	exit()

with fio('your_shapefile.shp', 'w', driver='ESRI Shapefile', crs=spatial_ref, schema=schema, encoding='utf-8') as dst:
	for i, geometry in enumerate(j["features"]):
		if geometry is None:
			continue
		print(geometry['properties']['S_Name'])
		feature = {'geometry': geometry['geometry'], 'properties': geometry['properties']}
		dst.write(feature)


