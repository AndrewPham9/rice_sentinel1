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
import same_shape
from datetime import datetime

def getArray(inRaster):
	raster = gdal.Open(inRaster)
	band = raster.GetRasterBand(1)
	array_val = band.ReadAsArray()
	date = int (inRaster.split('/')[-1].split('_')[-1].split('.')[0])
	dim = array_val.shape

	return (array_val, date, dim)

def filter_NaN (array):
	for element in array:
		if element != '--':
			return element


#run for a 3d matrix of value and matrix of dates:
def run (matrix, date, tiff_model):
	matrix_2 = scipy_ndim.filters.gaussian_filter(matrix, (1,0,0))
	for matrix in matrix_2:
		path = tiff_model.replace()
		config_this.createTiff(matrix, tiff_model, )
	# matrix_2 = matrix
	# matrix_rot = np.rot90(matrix,k=1,axes=(0,2))
	# matrix_rot_2 = np.rot90(matrix_2,k=1,axes=(0,2))
	# date_rot = np.rot90(date,k=1,axes=(0,2))
	# #create an image of min and max value
	# amin = np.amin(matrix_2, 0)
	# amax = np.amax(matrix_2, 0)

	# #create an image of start date
	# condition1 = (matrix_2[:,:,]!=amin)
	# DoS = np.ma.masked_where(condition1, date)
	# DoS[DoS.mask] = 0

	# A = np.zeros(DoS[0].shape)
	# for i in range (DoS.shape[0]):
	# 	A = A + DoS[i]
	# DoS = A


	# # create an image of maximum date
	# condition2 = (matrix_2[:,:,]!=amax)
	# DoM = np.ma.masked_where(condition2, date)
	# DoM[DoM.mask] = 0
	# B = np.zeros(DoM[0].shape)
	# for i in range (DoM.shape[0]):
	# 	B = B + DoM[i]
	# DoM = B
	# for i in 
	#create an image of max_date - min_date
	# LoS = DoM - DoS
	# Rice = np.ones(DoM.shape)
	# condition_LoS = (LoS[:,:] < 50)

	# Rice = np.ma.masked_where(condition_LoS, Rice)
	# Rice[Rice.mask] = 0

	#threshold of max
	# condition_max = (amax[:,:] < -15)
	# Rice = np.ma.masked_where(condition_max, Rice)
	# Rice[Rice.mask] = 0

	# # condition_max2 = (amax[:,:] > -14.5)
	# # Rice = np.ma.masked_where(condition_max2, Rice)
	# # Rice[Rice.mask] = 0

	# #thres hold of min
	# condition_min = (amin[:,:] > -20)
	# Rice = np.ma.masked_where(condition_min, Rice)
	# Rice[Rice.mask] = 0

	# # condition_min = (amin[:,:] < -21.5)
	# # Rice = np.ma.masked_where(condition_min, Rice)
	# # Rice[Rice.mask] = 0

	# #
	# max_min = amax - amin
	# condition_max_min = (max_min[:,:] < 6)
	# Rice[Rice.mask] = 0

	# #write all above image to disk (3image)

	# rice_path = tiff_model.replace(os.path.basename(tiff_model), 'rice.TIF')
	# config_this.createTiff(Rice, tiff_model, rice_path)

	

me.strptime(d1, "%Y%m%d")
    d2 = datetime.strptime(d2, "%Y%m%d")
    return abs((d2 - d1).days)


three_val = tuple(three_val)
three_val = np.stack(three_val,axis = 0)
#find max dim to create a date matrix
dim = np.amax(dims,0)
for date in dates:
	three_date.append(np.ones(dim) * days_between(str(date),str(dates[0])))


run (three_val, three_date, inRasters[0])

### why gdal warp create image of different shape (size)

