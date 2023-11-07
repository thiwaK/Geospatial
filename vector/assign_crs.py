import arcpy
import os
import argparse
import sys


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

	if sys.version_info[0] < 3:
		sys.exit("Error: Python 3 is required to run this script.")
	
	parser = argparse.ArgumentParser(description='Assign CRS data to shapefiles.')
	parser.add_argument('input', type=str, help='Directory containing shapefiles or a single shapefile.')
	parser.add_argument('crs', type=str, help='EPSG code or path to vector/raster containing CRS data.')
	args = parser.parse_args()

	all_shp = []
	if os.path.isdir(args.input):
		all_shp = get_shp(args.input)
	elif os.path.isfile(args.input) and args.input.endswith('.shp'):
		all_shp.append(args.input)
	else:
		sys.exit("Invalid input. Please provide a valid directory or shapefile.")

	target_crs = None
	if args.crs.isdigit():
		try:
			target_crs = arcpy.SpatialReference(int(args.crs))
		except Exception as e:
			raise e
			sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	elif os.path.isfile(args.crs):
		if check_crs(args.crs):
			target_describe = arcpy.Describe(args.crs)
			target_crs = target_describe.spatialReference
		else:
			sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	else:
		sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	print("")
	print(f"> CRS Name: {target_crs.name}")
	print(f"> CRS Factory Code: {target_crs.factoryCode}")
	print("")

	for shp in all_shp:
		print(f"Assigning... {os.path.basename(shp)}")
		arcpy.DefineProjection_management(shp, target_crs)
