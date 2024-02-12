import rioxarray as rx
import xarray as xr
from rioxarray.merge import merge_arrays
import os
from skimage import color, io, exposure, img_as_float
from skimage.exposure import match_histograms
import numpy as np
import gc

output = r"E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\merged_dataset.tif"
rasters = r"""
E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\20MAR04050707-M3DS_R1C2-014599910010_01_P002.TIF
E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\20MAR04050707-M3DS_R2C1-014599910010_01_P002.TIF
E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\20MAR04050707-M3DS_R2C2-014599910010_01_P002.TIF
E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\20MAR04050637-M3DS-014599910010_01_P001.TIF
E:\Spatial_Data\LandueManagement\Sattelite Image Kandy\2020\20MAR04050707-M3DS_R1C1-014599910010_01_P002.TIF
""".replace('"','').split('\n')

brightness_bands = 3

def adpt_eq(img, limits=0.1):
    'Adaptive Equalization'
    return exposure.equalize_adapthist(img, clip_limit=limits)

def gamma_corr(img, gamma=0.5, gain=1):
    'Gamma correction'
    return exposure.adjust_gamma(img, gamma=gamma, gain=gain)

def contrast_stretch(img, limits=(2, 98)):
    'Contrast stretching'
    p2, p98 = np.percentile(img, limits)
    return exposure.rescale_intensity(img, in_range=(p2, p98))

def equalize(img, band_count=3):
    'Equalization'
    eq_brightness_bands = np.zeros_like(img)
    for i in range(band_count):
        eq_brightness_bands[:, :, i] = exposure.equalize_hist(img[:, :, i])
    return eq_brightness_bands


# brightness_bands1 = img1[:, :, :brightness_bands]
# other_bands1 = img1[:, :, brightness_bands:]
# brightness_bands2 = img2[:, :, :brightness_bands]
# other_bands2 = img2[:, :, brightness_bands:]
# eq_brightness_bands1 = np.zeros_like(brightness_bands1)
# eq_brightness_bands2 = np.zeros_like(brightness_bands2)
# for i in range(3):
#     eq_brightness_bands1[:, :, i] = exposure.equalize_hist(brightness_bands1[:, :, i])
#     eq_brightness_bands2[:, :, i] = exposure.equalize_hist(brightness_bands2[:, :, i])
# adjusted_img1 = np.concatenate((eq_brightness_bands1, other_bands1), axis=2)
# adjusted_img2 = np.concatenate((eq_brightness_bands2, other_bands2), axis=2)
# io.imsave("adjusted_image1.tif", adjusted_img1)
# io.imsave("adjusted_image2.tif", adjusted_img2)

rasters = [raster.strip() for raster in rasters if raster.strip() and os.path.isfile(raster.strip())]
rio_imgs = [rx.open_rasterio(raster) for raster in rasters]

valid_band_count = False not in [rio_imgs[index].shape[0] == rio_imgs[index+1].shape[0] for index in range(len(rasters)-1)]
same_crs = False not in [rio_imgs[index].rio.crs == rio_imgs[index+1].rio.crs for index in range(len(rasters)-1)]
resolution = (abs(rio_imgs[0].rio.resolution()[0]), abs(rio_imgs[0].rio.resolution()[1]))
crs = rio_imgs[0].rio.crs
transforms = [raster.rio.transform() for raster in rio_imgs]
merge_only = 1

if not valid_band_count:
    raise ValueError("Datasets must have 4 bands!")

if not same_crs:
    raise ValueError("Datasets must have same crs!")

dims = ["band", "y", "x"]
merged_raster = None

if merge_only:
    merged_raster = merge_arrays(dataarrays=rio_imgs, 
                res=resolution, crs=crs, nodata=None)
else:
    
    img1 = rio_imgs[0]
    img1_corr = adpt_eq(img1, 0.5)
    img1_corr = gamma_corr(img1_corr, 0.01)
    img1_corr = img_as_float(img1_corr)
    img1_corr_geo = xr.DataArray(img1_corr, dims=dims).astype("float")\
            .rio.write_nodata(None).rio.write_transform(transforms[0]).rio.write_crs(crs)

    
    for index, img in enumerate(rio_imgs[1:]):
        img2_corr = match_histograms(img_as_float(img), img1_corr)
        img2_corr = xr.DataArray(img2_corr, dims=dims).astype("float")\
            .rio.write_nodata(None)\
            .rio.write_transform(transforms[index+1]).rio.write_crs(crs)

        if type(merged_raster) != type(None):
            merged_raster = merge_arrays(dataarrays=[merged_raster, img2_corr], 
                res=resolution, crs=crs, nodata=None)
            del img2_corr
            gc.collect()

        else:
            merged_raster = merge_arrays(dataarrays=[img1_corr_geo, img2_corr], 
                res=resolution, crs=crs, nodata=None)
            del img1_corr_geo
            del img2_corr
            gc.collect()

merged_raster.rio.to_raster(output)



