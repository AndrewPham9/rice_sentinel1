import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as scipy_ndim
from osgeo import gdal
from osgeo import ogr
import os
import config_this
import subprocess
import shutil
import glob
import config_this
from datetime import datetime
import kmean_for_rice

multi_raster_pth = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/angiang/stacked_multiTemporalFilter_rice_20190606.tif'

def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)


def rice_potential (multi_raster_pth):
	multi_raster = gdal.Open(multi_raster_pth)
	#return a 3d array of multi_raster
	multi_sigma0 = multi_raster.ReadAsArray()
	multi_dB = 10*np.log10(multi_sigma0)
	rice_matrix = np.std(multi_dB, 0)
	areas = list()
	#machine learning for deviation matrix
	for k in range(7):
		if k == 0:
			pass
		elif k == 1:
			pass
		else:
			area = kmean_for_rice.rice_image(rice_matrix, multi_raster_pth, 'hehe_rice_%s.tif'%(str(k)), k)
			areas.append(area)

rice_potential (multi_raster_pth)