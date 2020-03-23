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
import scipy.ndimage, scipy.signal
#get raster by shape
#return an matrix of image inside shp_path

np.set_printoptions(formatter={'float_kind':lambda x: "%.5f" % x})
def getRasByShape (raster_path, shp_path):
	shapefile = gpd.read_file(shp_path)
	geoms = shapefile.geometry.values
	geometry = geoms[0]
	geoms = [mapping(geoms[0])]
	with rasterio.open(raster_path) as src:
		out_image, out_transform = mask(src, geoms, crop=True)
	return out_image


#create X train from list of rasters inside an Shp
#each raster contain 1 feature
#return X.size = n*m (n is total number of pixels inside shp, m = features)
def create_X_train (list_Raster_pth, shp_pth):
	def list_to_tuple(list): 
		return (*list, )
	X = list()
	for i in range(len(list_Raster_pth)):
		Xi = getRasByShape(list_Raster_pth[i], shp_pth)
		Xi = Xi.reshape(Xi.shape[0],-1)
		X.append(Xi)

	X = list_to_tuple(X)
	X = np.concatenate(X, axis=0)
	bad = np.zeros (X.shape[0])
	# delete all pixel have nan as all feature
	X = X.transpose()
	X = np.delete(X, np.argwhere(X == bad), axis = 0)
	return X



# key = ['C:/Users/longdt/Desktop/Duy/project/rice/sr_code/Time_series_data/20190829_t/key.tif']
# print (type(key))
# shp_pth = 'C:/Users/longdt/Desktop/Duy/project/rice/input/train_shapefile/trained_rice_4326.shp'
# create_X_train(key, shp_pth)

#fit gaussian for X train and Y train, than predict X
def fit_gaussian (X_train, Y_train, X, result_shape, imageDim, out_raster_pth):
	#create an Gausian naive bayes objecet
	gnb = GaussianNB()
	gnb.fit(X_train, Y_train)
	Y = gnb.predict(X)
	Y = Y.reshape(result_shape)
	config_this.createTiff(Y, imageDim, out_raster_pth)
	return Y


# predic gaussian with list of roi = shp, feature = list_raster_pth, final raster_pth will have result_shape
# raster_pth to get metadata to create result tif, X is tuple of features
# return classification matrix
def pred_gaussian (raster_pth, shp_pths, X, list_Raster_pth, result_shape, out_raster_pth):
	# create many points with 3 feature 1,2,3 as X array
	# create X from feature X1, X2, X3
	X = np.concatenate(X, axis=1)
	#for train dataset X rice will be X_a, X no rice will be X_b , setdiff1d will mask out all zero/
	X_train = list()
	Y_train = list()
	i = 0
	for shp_pth in shp_pths:
		X_train_i = create_X_train(list_Raster_pth, shp_pth)
		X_train.append(X_train_i)
		Y_train.append(np.ones((X_train_i.shape[0],))*i)
		i+=1
	#here we have X_a is matrix with 3 feature and Y is label matrix for those feature
	#Now connect X_a and X_b to be X_train, Y-a and Y_b to be Y_train
	X_train = np.concatenate(tuple(X_train), axis=0)
	Y_train = np.concatenate(tuple(Y_train), axis=0)

	#create rice.tif from multi_raster_path metadata
	result = fit_gaussian(X_train, Y_train, X, result_shape, raster_pth, out_raster_pth)
	return result





