from osgeo import gdal, ogr
import os

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

