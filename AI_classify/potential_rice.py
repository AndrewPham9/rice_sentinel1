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
from AI_classify import config_MCL
import sys

# np.set_printoptions(threshold=sys.maxsize)
def linear_timeseries_image (matrix_3d, parts, rasterDim,child_fold):
	Y = np.reshape(matrix_3d, (matrix_3d.shape[0],-1))
	len_Y = Y.shape[1]
	chunk_matrixs = list()

	#split matrix to many chunk because lstsq can only word in some certain amount of pixel
	if (len_Y/parts)%1 == 0:
		chunk = int (len_Y/parts)
	else:
		chunk = int (len_Y/parts - (len_Y/parts)%1)

	for i in range(parts):
		if i == (parts - 1):
			chunk_matrix = Y[:,i*chunk:len_Y]
		else:
			chunk_matrix = Y[:,i*chunk:((i+1)*chunk)]
		chunk_matrixs.append(chunk_matrix)

	k_slope_dB_sorted = list()
	b_intercept = list()

	for chunk_matrix in chunk_matrixs:
		list
		X = np.arange(start=0, stop=chunk_matrix.shape[0], step=1)
		A = np.vstack([X, np.ones(len(X))]).T
		r = np.linalg.lstsq(A, chunk_matrix, rcond=-1)[0]
		k_slope_dB_sorted.append(r[0])
		b_intercept.append(r[1])

		# return [k_slope_dB_sorted, b_constant_dB_sorted]
	k_slope_dB_sorted = np.concatenate (k_slope_dB_sorted, axis = 0)
	b_intercept	= np.concatenate (b_intercept, axis = 0)

	k_slope_dB_sorted = k_slope_dB_sorted.reshape(matrix_3d.shape[1],matrix_3d.shape[2])	
	b_intercept = b_intercept.reshape(matrix_3d.shape[1],matrix_3d.shape[2])
	config_this.createTiff(k_slope_dB_sorted, rasterDim, '%s/k_intercept.tif'%(child_fold))
	config_this.createTiff(b_intercept, rasterDim, '%s/b_intercept.tif'%(child_fold))
	return ([k_slope_dB_sorted, b_intercept])


def get_std_b_k(raster_pth, child_fold):
	# 1 - std, 2 - k, 3 - b
	raster_arr = gdal.Open(raster_pth).ReadAsArray()
	dB = 10*np.log10(raster_arr)
	dB_sorted = np.sort(dB, axis=0, kind='quicksort', order=None)
	std_matrix = np.std(dB, 0)
	#create std tif
	config_this.createTiff(std_matrix, raster_pth, '%s/std.tif'%(child_fold))
	# create k and b tif
	k_slope_dB_sorted, b_constant_dB_sorted = linear_timeseries_image(dB_sorted, 25, raster_pth, child_fold)

	# get X features from 3 matrix
	X1, X2, X3 = std_matrix.reshape((-1, 1)), k_slope_dB_sorted.reshape((-1, 1)), b_constant_dB_sorted.reshape((-1, 1))
	X1, X2, X3 = np.nan_to_num(X1), np.nan_to_num(X2), np.nan_to_num(X3)
	#return 2 type, raster or array, get raster by shape need raster, createX need array
	return [(X1,X2,X3),['%s/std.tif'%(child_fold),'%s/k_intercept.tif'%(child_fold),'%s/b_intercept.tif'%(child_fold)],std_matrix.shape]




