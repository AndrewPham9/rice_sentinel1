import sys
sys.path.insert(1, '../')

import numpy as np
from osgeo import gdal
import os
import shutil
import glob
from datetime import datetime
import geopandas as gpd
from shapely.geometry import mapping
import rasterio
from rasterio.mask import mask
from sklearn.naive_bayes import GaussianNB
from config import config_this
import config_MCL
import sys
import potential_rice
import scipy.ndimage, scipy.signal
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import data_generate
# np.set_printoptions(threshold=sys.maxsize)
	
def get_X(raster_pth):
	mm_scaler = MinMaxScaler()
	# get gaussian smooth
	raster_arr = gdal.Open(raster_pth).ReadAsArray()
	dB = 10*np.log10(raster_arr)
	gaussian_smoothed = scipy.ndimage.gaussian_filter(dB, order = 0, sigma = 2)
	result_shape = gaussian_smoothed.shape
	# convert shape to count maxima and minima
	gaussian_smoothed = gaussian_smoothed.reshape(dB.shape[0],-1)
	gaussian_smoothed = gaussian_smoothed.transpose()

	# conut maxima and minina
	maxima = data_generate.count_maxima(gaussian_smoothed)
	minima = data_generate.count_minima(gaussian_smoothed)
	# reshape for scaling
	maxima = maxima.reshape((maxima.shape[0],1))
	minima = minima.reshape((minima.shape[0],1))
	
	# feature scaling
	gaussian_smoothed_scale = mm_scaler.fit_transform(gaussian_smoothed)
	maxima_scale = mm_scaler.fit_transform(maxima)
	minima_scale = mm_scaler.fit_transform(minima)

	# concatenate
	X_data = np.concatenate((gaussian_smoothed, maxima, minima), axis = 1)
	print (X_data.shape)
	return [X_data, raster_arr.shape]


