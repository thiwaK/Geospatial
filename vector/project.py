import arcpy
import os
import argparse

'''
	Require ArcGIS Pro - arcpy (python 3)
'''

def get_shp(directory):

	shp_files = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(".shp"):
				shp_files.append(os.path.join(root, file))

	return shp_files

def check_crs(shapefile_path):
	desc = arcpy.Describe(shapefile_path)
	if desc.SpatialReference is not None:
		return True
	else:
		return False

def check_crs_exists(crs_value):
	try:
		arcpy.SpatialReference(crs_value)
		return True
	except Exception as e:
		raise e
		return False



if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Convert one projection to another.')
	parser.add_argument('input', type=str, help='Directory containing shapefiles or a single shapefile.')
	parser.add_argument('crs', type=str, help='EPSG code or path to vector/raster containing CRS data.')
	parser.add_argument('output', type=str, help='Directory to store output shapefile.')
	args = parser.parse_args()

	all_shp = []
	if os.path.isdir(args.input):
		all_shp = get_shp(args.input)
	elif os.path.isfile(args.input) and args.input.endswith('.shp'):
		all_shp.append(args.input)
	else:
		print("Invalid input. Please provide a valid directory or shapefile.")
		exit()

	target_crs = None
	if args.crs.isdigit():
		try:
			target_crs = arcpy.SpatialReference(int(args.crs))
		except Exception as e:
			raise e
			print("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	elif os.path.isfile(args.crs):
		if check_crs(args.crs):
			target_describe = arcpy.Describe(args.crs)
			target_crs = target_describe.spatialReference
		else:
			print("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
			exit()
	else:
		print("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
		exit()

	if args.output and not os.path.exists(args.output):
		os.makedirs(args.output)
	if args.output is None:
		print("Missing required argument [output].")
		exit()

	print("")
	print(f"> CRS Name: {target_crs.name}")
	print(f"> CRS Factory Code: {target_crs.factoryCode}")
	print("")

	count = 1
	for shp in all_shp:
		print(f"    ...{os.path.basename(shp)}")
		out = os.path.join(args.output, os.path.basename(shp))
		arcpy.management.Project(shp, out, target_crs)
		count += 1