import geopandas as gpd
import os
import argparse
import concurrent.futures

def clip(source, clip_shp, output):

	if args.replace == None and os.path.isfile(output): 
		print(f"   skipping ...{os.path.basename(output)}")
		return

	source_shp = gpd.read_file(source)
	clipped_shp = gpd.clip(source_shp, clip_shp)
	if clipped_shp.empty:
		print(f"   skipping ...{os.path.basename(output)}")
	else:
		clipped_shp.to_file(output, driver="ESRI Shapefile")
		print(f"   saving ...{os.path.basename(output)}")

def get_shp(directory):
	shp_files = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(".shp"):
				shp_files.append(os.path.join(root, file))

	return shp_files

def get_output_file(shp, value_of_attr=None):
	if value_of_attr:
		if args.output is None:
			output = os.path.splitext(shp)[0] + "_clipped.shp"
			output = os.path.split(shp)[0] + value_of_attr + '_' + os.path.split(shp)[1]
		else:
			output = os.path.join(args.output, value_of_attr + '_' + os.path.basename(shp))
	else:
		if args.output is None:
			output = os.path.splitext(shp)[0] + "_clipped.shp"
		else:
			output = os.path.join(args.output, os.path.basename(shp))

	return output

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Create new Shapefile(s) that contains the features of the source that are within the spatial extent of the cutter.')
	parser.add_argument('input', type=str, help='Directory containing shapefiles.')
	parser.add_argument('cutter', type=str, help='Shapefiles to use as the cutter.')
	parser.add_argument('-a', '--attribute', type=str, help='Attribute name, if you have a multipolygon cutter.')
	parser.add_argument('-v', '--value', help='Spacific attribute value that only need to clip features.')
	parser.add_argument('-o', '--output', type=str, help='Output directory.')
	parser.add_argument('-r', '--replace', help='Overwrite existing files.', action='store_true')
	
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
	executor = concurrent.futures.ThreadPoolExecutor()
	print(f">  max_threads: {executor._max_workers}")
	print(f">  cutter: {os.path.basename(cutter)}")
	print(">  start clipping...")

	executor.shutdown()
	clip_shp = gpd.read_file(cutter)

	with concurrent.futures.ThreadPoolExecutor() as executor:

		if args.attribute:
			try:
				clip_shp = clip_shp.sort_values(args.attribute, ascending=False).drop_duplicates(['geometry'])
			except Exception as e:
				print("Invalid attribute name.")
				exit()
			
			for index, row in clip_shp.iterrows():
				value_ = row[args.attribute]
				geom_ = row['geometry']

				for shp in all_shp:
					if args.value:
						if args.value in value_:
							output = get_output_file(shp, value_)
							executor.submit(clip, shp, geom_, output)
					else:
						output = get_output_file(shp, value_)
						executor.submit(clip, shp, geom_, output)
		else:
			for shp in all_shp:
				output = get_output_file(shp)
				executor.submit(clip, shp, clip_shp, output)