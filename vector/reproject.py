import arcpy
import os, sys, shutil
import argparse

def get_shp(directory):

	shp_files = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(".shp"):
				shp_files.append(os.path.join(root, file))

	return shp_files

def check_crs(shapefile_path):
	desc = arcpy.Describe(shapefile_path)
	return desc.SpatialReference

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
		sys.exit("Invalid input. Please provide a valid directory or shapefile.")

	target_crs = None
	if args.crs.isdigit():
		try:
			target_crs = arcpy.SpatialReference(int(args.crs))
		except Exception as e:
			raise e
			sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	elif os.path.isfile(args.crs):
		crs = check_crs(args.crs)
		if crs:
			target_crs = crs
		else:
			sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")
	else:
		sys.exit("Invalid CRS input. Please valid EPSG code or a path to a file containing CRS data.")

	if args.output and not os.path.exists(args.output):
		os.makedirs(args.output)
	elif args.output and os.path.exists(args.output):
		print(f"All files in {args.output} will be deleted. Press Enter to continue.")
		input()
		shutil.rmtree(args.output)
		os.makedirs(args.output)
	if args.output is None:
		sys.exit("Missing required argument [output].")

	print("")
	print(f"> CRS Name: {target_crs.name}")
	print(f"> CRS Factory Code: {target_crs.factoryCode}")
	print("")

	for shp in all_shp:

		shp_crs = check_crs(shp)
		if shp_crs.factoryCode == target_crs.factoryCode:
			print(f"    ...{os.path.basename(shp)} already in {target_crs.name}. Skipping...")
			continue

		out = os.path.join(args.output, os.path.basename(shp))
		if os.path.isfile(out):
			os.remove(out)

		print(f"    ...{os.path.basename(shp)} current CRS: {check_crs(shp).name}")
		arcpy.management.Project(shp, out, target_crs)