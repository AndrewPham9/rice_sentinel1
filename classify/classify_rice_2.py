import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as scipy_ndim
from osgeo import gdal
from osgeo import ogr
import os

import subprocess
import shutil
import glob

from datetime import datetime

def classify (inRaster):
	three_D_val = list()
	raster = gdal.Open(inRaster)
	for i in range (raster.RasterCount):
		band = raster.GetRasterBand(i+1)
		array_val = band.ReadAsArray()
		three_D_val.append(array_val)

	three_D_val = tuple(three_D_val)
	three_D_val = np.stack(three_D_val,axis = 0)
	print (three_D_val)


inRaster = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/classify/doq_index.tif'
classify(inRaster)