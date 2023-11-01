import arcpy
import os
import argparse

'''
	Require ArcGIS Pro - arcpy (python 3)
'''

class progress():
		def __init__(self, current, maximum):
				self.current = current
				self.maximum = maximum
				self.BAR_WIDTH = 15
				self.FILE_NAME_LEN = 30
				
				self.current -=1
				self.next("")
				
				
		def next(self, file_name):
				self.current += 1
				x = int((self.BAR_WIDTH + self.FILE_NAME_LEN)*self.current/self.maximum)
				y = round(self.current/self.maximum*100, 1)
				z = file_name[(self.FILE_NAME_LEN*-1):]
				text_pb = "{}[{}{}] {}/{} {}%".format("Processing", "#"*x, "."*(self.BAR_WIDTH+self.FILE_NAME_LEN-x), self.current, self.maximum, y)
				print(text_pb, end='\r', file=sys.stdout, flush=True)

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
	
	parser = argparse.ArgumentParser(description='Assign CRS data to shapefiles.')
	parser.add_argument('input', type=str, help='Directory containing shapefiles or a single shapefile')
	parser.add_argument('crs', type=str, help='EPSG code or path to shapefile containing CRS data (ex.5234)')
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
			print("Invalid CRS input. Please valid EPSG code or a path to a shapefile containing CRS data.")
	elif os.path.isfile(args.crs) and args.crs.endswith('.shp'):
		if check_crs(args.crs):
			target_describe = arcpy.Describe(args.crs)
			target_crs = target_describe.spatialReference
		else:
			print("Invalid CRS input. Please valid EPSG code or a path to a shapefile containing CRS data.")
			exit()
	else:
		print("Invalid CRS input. Please valid EPSG code or a path to a shapefile containing CRS data.")
		exit()
	print("")
	print(f"> CRS Name: {target_crs.name}")
	print(f"> CRS Factory Code: {target_crs.factoryCode}")
	print("")

	p = progress(0, len(all_shp))
	count = 0
	for shp in all_shp:
		arcpy.DefineProjection_management(shp, target_crs)
		count += 1
		p.next(shp)