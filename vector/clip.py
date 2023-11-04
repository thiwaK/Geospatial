import geopandas as gpd
import os
import argparse

def clip(source, clip_shp, clipped):
	source_shp = gpd.read_file(source)
	clipped_shp = gpd.clip(source_shp, clip_shp)
	clipped_shp.to_file(clipped, driver="ESRI Shapefile")

def get_shp(directory):
	shp_files = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(".shp"):
				shp_files.append(os.path.join(root, file))

	return shp_files


if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='This will create a new Shapefile that contains the features of the source that are within the spatial extent of the cutter.')
	parser.add_argument('input', type=str, help='Directory containing shapefiles.')
	parser.add_argument('cutter', type=str, help='Shapefiles to use as the cutter.')
	parser.add_argument('-o', '--output', type=str, help='Output directory.')
	args = parser.parse_args()

	all_shp = []
	cutter = None
	if os.path.isdir(args.input):
		all_shp = get_shp(args.input)
	else:
		print("Invalid input. Please provide a valid directory.")
		exit()

	if os.path.isfile(args.cutter) and args.cutter.endswith('.shp'):
		cutter = args.cutter
	else:
		print("Invalid input. Please provide a valid shapefile.")
		exit()

	if args.output and not os.path.exists(args.output):
		os.makedirs(args.output)


	print("")
	print(f"> Cutter: {os.path.basename(cutter)}")
	print("> Clipping...")
	clip_shp = gpd.read_file(cutter)


	for shp in all_shp:
		
		if args.output is None:
			output = os.path.splitext(shp)[0] + "_clipped.shp"
		else:
			output = os.path.join(args.output, os.path.basename(shp))
		print(f"    ...{os.path.basename(output)}")
		clip(shp, clip_shp, output)