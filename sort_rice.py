import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as scipy_ndim
from osgeo import gdal
from osgeo import ogr
import os

def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)


multi_raster_pth = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/angiang/stacked_multiTemporalFilter_rice_20190606.tif'
	
multi_raster = gdal.Open(multi_raster_pth)
#return a 3d array of multi_raster
multi_sigma0 = multi_raster.ReadAsArray()
multi_dB = 10*np.log10(multi_sigma0)
dB_sorted = np.sort(multi_dB, axis=0, kind='quicksort', order=None)


def linear_timeseries_image (matrix_3d, parts, rasterDim):
	Y = np.reshape(matrix_3d, (matrix_3d.shape[0],-1))
	len_Y = Y.shape[1]
	print (len_Y)
	chunk_matrixs = list()

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
	b_constant_dB_sorted = list()

	for chunk_matrix in chunk_matrixs:
		X = np.arange(start=0, stop=chunk_matrix.shape[0], step=1)
		A = np.vstack([X, np.ones(len(X))]).T
		r = np.linalg.lstsq(A, chunk_matrix, rcond=-1)[0]
		k_slope_dB_sorted.append(r[0])
		b_constant_dB_sorted.append(r[1])
		# return [k_slope_dB_sorted, b_constant_dB_sorted]
	k_slope_dB_sorted = np.concatenate (k_slope_dB_sorted, axis = 0)
	b_constant_dB_sorted = np.concatenate (b_constant_dB_sorted, axis = 0)

	k_slope_dB_sorted = k_slope_dB_sorted.reshape(matrix_3d.shape[1],matrix_3d.shape[2])	
	b_constant_dB_sorted = b_constant_dB_sorted.reshape(matrix_3d.shape[1],matrix_3d.shape[2])

	return ([k_slope_dB_sorted, b_constant_dB_sorted])
	# print (k_slope_dB_sorted.shape)
	# print (b_constant_dB_sorted.shape)
	# createTiff(k_slope_dB_sorted, rasterDim, 'k_slope_dB_sorted.tif')
	# createTiff(b_constant_dB_sorted, rasterDim, 'b_constant_dB_sorted.tif')

linear_timeseries_image(dB_sorted, 25, multi_raster_pth)
# createTiff(k_slope_dB_sorted, multi_raster_pth, 'k_slope_dB_sorted.tif')
# createTiff(b_constant_dB_sorted, multi_raster_pth, 'b_constant_dB_sorted.tif')

