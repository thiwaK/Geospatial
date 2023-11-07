from osgeo import gdal, ogr, osr
import os, argparse


def raster_to_point(input_raster, output_shapefile, band=1, filed='value'):

	raster_dataset = gdal.Open(input_raster)
	if raster_dataset is None:
		print("Could not open the raster dataset.")
		return

	band = raster_dataset.GetRasterBand(band)

	driver = ogr.GetDriverByName('ESRI Shapefile')
	if driver is None:
		print("Driver not available.")
		return

	output_ds = driver.CreateDataSource(output_shapefile)
	if output_ds is None:
		print("Could not create the output data source.")
		return

	output_layer = output_ds.CreateLayer("points", geom_type=ogr.wkbPoint)
	if output_layer is None:
		print("Could not create the output layer.")
		return

	# proj.db error. Could not add src to output
	# srs = osr.SpatialReference()
	# srs.ImportFromWkt(raster_dataset.GetProjection())
	# output_layer.SetSpatialRef(srs)

	# print(" :", srs.GetAttrValue('PROJCS'))

	field_defn = ogr.FieldDefn(filed, ogr.OFTInteger)
	output_layer.CreateField(field_defn)

	transform = raster_dataset.GetGeoTransform()
	x_size = transform[1]
	y_size = transform[5]

	for y in range(raster_dataset.RasterYSize):
		for x in range(raster_dataset.RasterXSize):
			value = band.ReadAsArray(x, y, 1, 1)[0, 0]
			if value != band.GetNoDataValue():
				x_coord = transform[0] + (x + 0.5) * x_size
				y_coord = transform[3] + (y + 0.5) * y_size

				point = ogr.Geometry(ogr.wkbPoint)
				point.AddPoint(x_coord, y_coord)
				# point.AssignSpatialReference(srs)

				feature = ogr.Feature(output_layer.GetLayerDefn())
				feature.SetGeometry(point)
				feature.SetField(filed, int(value))
				output_layer.CreateFeature(feature)
				feature = None

	output_ds = None
	raster_dataset = None

def get_tif_files(directory_path):
	tif_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.tif')]
	return tif_files

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert a raster file to a point shapefile.')
	parser.add_argument('input', help='Path to a directory containing tif files or a single tif.')
	parser.add_argument('output', help='Path to the output directory.')
	parser.add_argument('-b', '--band', type=int, default=1, help='The band to be processed. Default is 1.')
	parser.add_argument('-f', '--field', default='value', help='Field name for the output shapefile. Default is "value".')
	args = parser.parse_args()

	all_tif = []
	if os.path.isdir(args.input):
		all_tif = get_tif_files(args.input)
	elif os.path.isfile(args.input) and args.input.endswith('.tif'):
		all_tif.append(args.input)
	else:
		print("Invalid input. Please provide a valid directory or a tif.")
		exit()

	if args.output and not os.path.exists(args.output):
		os.makedirs(args.output)
		print("Creating output directory")

	for tif in all_tif:
		output_shp = os.path.join(args.output, os.path.splitext(os.path.basename(tif))[0] + ".shp")
		print(f"{os.path.basename(tif)} --> {os.path.basename(output_shp)}")
		raster_to_point(tif, output_shp, args.band, args.field)