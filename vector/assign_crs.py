import arcpy
import os

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



# setup pathc
target_shp = r"E:\Spatial_Data\LK\50K\SHP\admin_ARC.shp"
base = r"E:\Spatial_Data\LK\50K\tiles\shp"

# get target_shp from target shapefile
target_describe = arcpy.Describe(target_shp)
target_crs = target_describe.spatialReference
target_crs_name = target_crs.Name


def get_shp(directory):

	shp_files = []
	for root, directories, files in os.walk(directory):
		for file in files:
			if file.endswith(".shp"):
				shp_files.append(os.path.join(root, file))

	return shp_files

all_shp = get_shp(base)
p = progress(0, len(all_shp))
count = 0
for shp in all_shp:
	arcpy.DefineProjection_management(shp, target_crs)
	count += 1
	p.next(shp)