from fiona import open as fio
import json, os
import codecs
import sys
import time

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout.buffer)
os.environ["PROJ_LIB"] = r"D:\Programs\QGIS 3.28.3\share\proj"

input_f  = sys.argv[1]
output_f = os.path.splitext(input_f)[0] + ".shp"

with open(input_f, encoding='utf-8') as f:
	js_obj = json.load(f)

schema = []
spatial_ref = js_obj['crs']['properties']['name']
attribute   = js_obj["features"][0]["properties"]
geometry_type    = js_obj["features"][0]['geometry']['type']

for feature in attribute:
	if type(feature) == str:
		schema.append((feature, 'str'))
	elif type(feature) == int:
		schema.append((feature, 'int'))
	else:
		schema.append((feature, 'str'))

schema = list(set(schema))
schema = {
	'geometry': geometry_type,
	'properties': schema
}


print(f"Output ../{os.path.basename(output_f)}")
total = len(js_obj["features"])-1
prefix = "Writing... "
bar_width = 60
start = time.time()

with fio(output_f, 'w', driver='ESRI Shapefile', crs=spatial_ref, schema=schema, encoding='utf-8') as dst:
	for i, item in enumerate(js_obj["features"]):
		_, _, geometry, properties = item.values()
		if geometry is None: continue
		dst.write({'geometry': geometry, 'properties': properties})

		x = int(i/total*bar_width)
		elapsed = time.time() - start

		mins, sec = divmod(elapsed, 60)
		time_str = f"{int(mins):02}:{int(sec):02}"
		
		print(f"{prefix}[{u'■'*x}{('·'*(bar_width-x))}] {int(i/total*100)}% {time_str}", end='\r', file=sys.stdout, flush=True)

