import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal
from osgeo import ogr
import os
import subprocess
import shutil
import glob
from datetime import datetime
import sort_rice
import geopandas as gpd
from shapely.geometry import mapping
import rasterio
from rasterio.mask import mask
from sklearn.naive_bayes import GaussianNB


def getRasByShape (raster_path, shp_path):
	shapefile = gpd.read_file(shp_path)
	geoms = shapefile.geometry.values
	geometry = geoms[0]
	geoms = [mapping(geoms[0])]
	with rasterio.open(raster_path) as src:
		out_image, out_transform = mask(src, geoms, crop=True)
	return out_image

def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)

def rice_image(X_train, Y_train, X, result_shape, imageDim, outband):
	#create an Gausian naive bayes objecet
	gnb = GaussianNB()
	gnb.fit(X_train, Y_train)
	print (X_train.shape)
	print (Y_train.shape)
	print (X.shape)
	Y = gnb.predict(X)
	Y = Y.reshape(result_shape)
	createTiff(Y, imageDim, outband)


def create_X_train (rast_pth1, rast_pth2, rast_pth3, shp_pth):
	#1,2,3 tif is 3 feature_space for rice
	X1 = getRasByShape(rast_pth1, shp_pth).reshape((-1, 1))
	X2 = getRasByShape(rast_pth2, shp_pth).reshape((-1, 1))
	X3 = getRasByShape(rast_pth3, shp_pth).reshape((-1, 1))
	X1, X2, X3 = np.nan_to_num(X1,0), np.nan_to_num(X2, 0), np.nan_to_num(X3, 0)

	X = np.concatenate((X1,X2,X3), axis=1)
	X = np.delete(X, np.argwhere(X == [0,0,0]), axis = 0)
	return X

def rice_potential (multi_raster_pth, shp_rice_pth, shp_norice_pth):

	multi_raster = gdal.Open(multi_raster_pth)
	multi_sigma0 = multi_raster.ReadAsArray() #3d array of multi_raster
	multi_dB = 10*np.log10(multi_sigma0)
	dB_sorted = np.sort(multi_dB, axis=0, kind='quicksort', order=None)
	std_matrix = np.std(multi_dB, 0)

	createTiff(std_matrix, multi_raster_pth, 'output/1.tif')
	k_slope_dB_sorted, b_constant_dB_sorted = sort_rice.linear_timeseries_image(dB_sorted, 25, multi_raster_pth)

	# 1 - std, 2 - k, 3 - b
	# create many points with 3 feature 1,2,3 as X array
	result_shape = std_matrix.shape
	X1, X2, X3 = std_matrix.reshape((-1, 1)), k_slope_dB_sorted.reshape((-1, 1)), b_constant_dB_sorted.reshape((-1, 1))
	X1, X2, X3 = np.nan_to_num(X1), np.nan_to_num(X2), np.nan_to_num(X3)
	X = np.concatenate((X1,X2,X3), axis=1)

	#for train dataset X rice will be X_a, X no rice will be X_b , setdiff1d will mask out all zero
	X_a = create_X_train('output/1.tif','output/2.tif','output/3.tif', shp_rice_pth)
	X_b = create_X_train('output/1.tif','output/2.tif','output/3.tif', shp_norice_pth)

	#for X_a will be classified as 1, X_b will be classified as 0
	Y_a = np.ones((X_a.shape[0],))
	Y_b = np.zeros((X_b.shape[0],))

	#here we have X_a is matrix with 3 feature and Y is label matrix for those feature
	#Now connect X_a and X_b to be X_train, Y-a and Y_b to be Y_train
	X_train = np.concatenate((X_a,X_b), axis=0)
	Y_train = np.concatenate((Y_a,Y_b), axis=0)

	#create rice.tif from multi_raster_path metadata
	area = rice_image(X_train, Y_train, X, result_shape, multi_raster_pth, 'rice.tif')
