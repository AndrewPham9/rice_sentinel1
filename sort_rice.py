import numpy as np
import matplotlib.pyplot as plt
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



def linear_timeseries_image (matrix_3d, parts, rasterDim):
	Y = np.reshape(matrix_3d, (matrix_3d.shape[0],-1))
	len_Y = Y.shape[1]
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
	createTiff(k_slope_dB_sorted, rasterDim, 'output/2.tif')
	createTiff(b_constant_dB_sorted, rasterDim, 'output/3.tif')
	return ([k_slope_dB_sorted, b_constant_dB_sorted])

# linear_timeseries_image(dB_sorted, 25, multi_raster_pth)
# createTiff(k_slope_dB_sorted, multi_raster_pth, 'k_slope_dB_sorted.tif')
# createTiff(b_constant_dB_sorted, multi_raster_pth, 'b_constant_dB_sorted.tif')

