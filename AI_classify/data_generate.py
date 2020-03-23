import sys
sys.path.insert(1, '../')

import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from osgeo import gdal
from tensorflow.python.keras.optimizers import RMSprop
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
import geopandas as gpd
from shapely.geometry import mapping
import rasterio
from rasterio.mask import mask
import config_MCL
import scipy.ndimage, scipy.signal
from config import config_this


# m = pixel inside roi
# return X data inside shp after scaling of time series
# time series need to be smoothed by gaussian
def create_X_multiband(raster_pth, shp_pth):
	X_data = config_MCL.create_X_train(raster_pth, shp_pth)
	X_data = 10*np.log10(X_data)
	X_data = scipy.ndimage.gaussian_filter(X_data, order = 0, sigma = 2)
	mm_scaler = MinMaxScaler()
	X_data_scale = mm_scaler.fit_transform(X_data)
	return [X_data, X_data_scale]

def count_maxima(gaussian_smoothed):
	#maxima
	local_max = scipy.signal.argrelextrema(gaussian_smoothed, np.greater, axis = 1)
	#count maxima
	unique, counts = np.unique(local_max[0], return_counts=True)
	dataset = pd.DataFrame({'location': unique, 'frequency': counts})
	dataset2 = pd.DataFrame({'location': np.arange(gaussian_smoothed.shape[0]), 'zeros':np.zeros(gaussian_smoothed.shape[0])})
	local_max = pd.merge(dataset2,dataset, on='location', how='left')
	#fill where no maxima = 0
	local_max = local_max.fillna(0)
	local_max = local_max['frequency'].to_numpy()
	return local_max

def count_minima(gaussian_smoothed):
	#minima
	local_min = scipy.signal.argrelextrema(gaussian_smoothed, np.less, axis = 1)
	#count minima
	unique, counts = np.unique(local_min[0], return_counts=True)
	dataset = pd.DataFrame({'location': unique, 'frequency': counts})
	dataset2 = pd.DataFrame({'location': np.arange(gaussian_smoothed.shape[0]), 'zeros':np.zeros(gaussian_smoothed.shape[0])})
	local_min = pd.merge(dataset2,dataset, on='location', how='left') 
	local_min = local_min.fillna(0)
	local_min = local_min['frequency'].to_numpy()
	return local_min

# create X inside shp and label by shp
def create_X_Y(raster_pth, shp_pths):
	X_data, Y_data = list(), list()
	i = 1
	for shp_pth in shp_pths:
		mm_scaler = MinMaxScaler()
		gaussian_smoothed, gaussian_smoothed_scale = create_X_multiband([raster_pth], shp_pth)
		shape = gaussian_smoothed.shape[0]
		# reshape a list back to an image matrix
		maxima  = count_maxima(gaussian_smoothed).reshape((shape,1))
		maxima_scale = mm_scaler.fit_transform(maxima)
		# reshape a list back to an image matrix
		minima  = count_minima(gaussian_smoothed).reshape((shape,1))
		minima_scale = mm_scaler.fit_transform(minima)
		X = np.concatenate((gaussian_smoothed_scale, maxima_scale, minima_scale), axis = 1)
		Y = np.ones(X.shape[0],)*i
		X_data.append(X)
		Y_data.append(Y)
		i+=1
	X_data = np.concatenate(X_data, axis = 0)
	Y_data = np.concatenate(Y_data, axis = 0)
	Y_data = Y_data.reshape((Y_data.shape[0],1))
	ohe    = OneHotEncoder()
	Y_data = ohe.fit_transform(Y_data).toarray()
	return [X_data,Y_data]

def split_train_test(XY_data):
	n_feature = XY_data[0].shape[1]
	#concatenate to shuffle X together with Y, then split X and Y back to it normal form
	X_Y = np.concatenate(tuple(XY_data), axis=1)
	np.random.shuffle(X_Y)
	# get X_data back from X_Y
	X_data = X_Y[:,0:n_feature]
	Y_data = X_Y[:,n_feature:]
	# use 0.8 to train, 0.2 to test
	train_split	= 0.8
	num_train	= int(train_split * len(X_data))

	X_train, X_test = X_data[0:num_train], X_data[num_train:]
	Y_train, Y_test = Y_data[0:num_train], Y_data[num_train:]

	train_data		= [X_train, Y_train]
	validation_data = [X_test, Y_test]
	return [train_data, validation_data]


# raster_fold contain many time series (multiband raster), this function will get data inside ROI for each time serires inteveral
def create_XY_timeseries (raster_fold, shp_pths):
	X_data = list()
	Y_data = list()
	for raster_pth in raster_pths:
		XY_data = create_X_Y(raster_pth, shp_pths)
		X_data.append(XY_data[0])
		Y_data.append(XY_data[1])
	X_data = np.concatenate(X_data, axis = 0)
	Y_data = np.concatenate(Y_data, axis = 0)
	return [X_data, Y_data]

# no_rice_pth		= 'C:/Users/longdt/Desktop/Duy/project/rice/input/train_shapefile/trained_norice_4326.shp'
# rice_pth			= 'C:/Users/longdt/Desktop/Duy/project/rice/input/train_shapefile/trained_rice_4326.shp'
# shp_pths			= [no_rice_pth, rice_pth]
# raster_fold = 'C:/Users/longdt/Desktop/Duy/project/rice/output/Time_series_data'
# raster_pths = config_this.getFoldTiff(raster_fold)

# XY_data = create_XY_timeseries(raster_fold, shp_pths)
# train_data, validation_data = split_train_test(XY_data)

# X_train, Y_train = train_data[0], train_data[1]
# X_test, Y_test = validation_data[0], validation_data[1]

# outFolder = '../../output/X_Y_train/'

# file = 'X_train.npy'
# np.save(outFolder+file, X_train, allow_pickle=True, fix_imports=True)

# file = 'Y_train.npy'
# np.save(outFolder+file, Y_train, allow_pickle=True, fix_imports=True)

# file = 'X_test.npy'
# np.save(outFolder+file, X_test, allow_pickle=True, fix_imports=True)

# file = 'Y_test.npy'
# np.save(outFolder+file, Y_test, allow_pickle=True, fix_imports=True)