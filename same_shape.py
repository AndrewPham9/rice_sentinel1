import numpy as np
from osgeo import gdal
from osgeo import ogr
import config_this
import subprocess
import shutil
import os
import glob
import config_this



def change(file_1, file_2):
    os.remove(file_1)
    os.rename(file_2, file_1)

def get_dim (inRaster):
	raster = gdal.Open(inRaster)
	band = raster.GetRasterBand(1)
	array_val = band.ReadAsArray()

	date = os.path.basename(inRaster).split('_')[2].split('.')[0]
	dim = array_val.shape
	return list(dim)

def find_abnomal_shape (inRasters):
	dim_buffer = list()
	path = list()
	path_buffer1 = list()
	path_buffer2 = list()

	for inRaster in inRasters:
		inRaster = inRaster.replace('//','/')
		dim_buffer.append(get_dim(inRaster))
		path.append(inRaster)

	dim_buffer = np.array(dim_buffer)
	dim_max = np.amax(dim_buffer, 0)
	print (dim_max)
	condition1 = np.where(dim_buffer[:,:] != dim_max)
	#chua toi uu lam
	condition2 = np.where(dim_buffer[:,:] == dim_max)
	locations = condition1[0]
	A = list(condition2[0])
	for i in range(len(A)):
		k = i+1
		if A[i] == A[k]:
			path_buffer1.append(path[A[i]])
			print (path[A[i]])
			break


	

	for location in locations:
		#do something with path_buffer element if the shape is abnomal
		path_buffer2.append(path[location])
	return (path_buffer1, path_buffer2)


def mosaic(list_img1, list_img2):
	py = config_this.config(section='py_machine')
	py_scripts = py['py_3_scripts']
	alpha = '0'

	for img in list_img2:
		outRaster = img.replace('.tif', '_shapeFixed.tif')
		command="py -3 "+py_scripts+"/gdal_merge.py -o "+outRaster+" -of GTiff -ot Float32 -n " + alpha + " -a_nodata NaN "+ list_img1[0] + ' ' + img

		print (outRaster)
		p1 = subprocess.Popen(command,shell=True)
		p1.wait()
		change (img, outRaster)

def same_shape(inRasters):
	A = find_abnomal_shape (inRasters)
	mosaic(A[0],A[1])
