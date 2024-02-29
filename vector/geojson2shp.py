import shapely.geometry as sg
from fiona import open as fio
import json, os
import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout.buffer)
os.environ["PROJ_LIB"] = r"D:\Programs\QGIS 3.28.3\share\proj"

_latestWkid_ = None
_id_ = None
_coordinates_ = None
_properties_ = None

def get_files(directory, ext):
	files_ = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(f".{ext}"):
				files_.append(os.path.join(root, file))

with open(sys.argv[1], encoding='utf-8') as f:
	j = json.load(f)

features = []
schema = []
for index, item in enumerate(j["results"]):
	attribute = item["attributes"]
	coordinates = item['geometry']['rings']
	spatial_ref = item['geometry']['spatialReference']['latestWkid']

	for feature in attribute:
		if type(feature) == str:
			schema.append((feature, 'str'))
		elif type(feature) == int:
			schema.append((feature, 'int'))
		else:
			schema.append((feature, 'str'))

		attribute[feature] = attribute[feature].strip()

	_id_ = index
	_coordinates_ = coordinates
	_properties_ = attribute
	_latestWkid_ = f"EPSG:{spatial_ref}"

	feature = {
		"type" : "Polygon",
		"id" : _id_,
		"geometry" : {
			"type" : "Polygon",
			"coordinates" : _coordinates_,
		},
		
		"properties" : _properties_,
	}

	features.append(feature)

schema = set(schema)
schema = list(schema)
schema = {
	'geometry': 'Polygon',
	'properties': schema
}

geo_json = {
	"type" : "FeatureCollection",
	"crs" : {
		"type" : "name",
		"properties" : {
			"name" : _latestWkid_,
		}
	}
}
geo_json['features'] = features



if len(schema['properties']) != len(features[0]['properties']):
	print("Schema Error")
	exit()

with fio('your_shapefile.shp', 'w', driver='ESRI Shapefile', crs=_latestWkid_, schema=schema, encoding='utf-8') as dst:
	for i, geometry in enumerate(features):
		if geometry is None:
			continue
		print(geometry['properties']['GND_NAME_Gaz'])
		feature = {'geometry': geometry['geometry'], 'properties': geometry['properties']}
		dst.write(feature)


