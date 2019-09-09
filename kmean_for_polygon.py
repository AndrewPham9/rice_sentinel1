from sklearn import cluster
from osgeo import gdal
import numpy as np
import subprocess
import config_this
import os

tiff_path = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/No_clip/hehe6_15.tif'
shapefile_path = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/angiang/train/trained_rice.shp'


def clip (shp, inRaster, outRaster):
    cmdLine2 = "gdalwarp -cutline " +shp + " -crop_to_cutline -of Gtiff -dstnodata 9999 -overwrite " + inRaster + ' ' + outRaster 
    p1 = subprocess.Popen(cmdLine2,shell=True)
    p1.wait()
    return outRaster

def get_rice_layers(tiff_path, shapefile_path):
	clip(shapefile_path, tiff_path, 'yolo.tif')
	dataset = gdal.Open('yolo.tif')

	band = dataset.GetRasterBand(1)
	img = band.ReadAsArray()
	unique, counts = np.unique(img, return_counts=True)

	unique = unique.tolist()
	counts = counts.tolist()
	unique.pop(-1)
	counts.pop(-1)

	a = len(counts)
	unique = np.array(unique)
	counts = np.array(counts)
	counts = counts.reshape(len(counts),1)

	kmeans_cluster = cluster.KMeans(n_clusters=2, max_iter = 10)
	kmeans_cluster.fit(counts)
	cluster_labels = kmeans_cluster.labels_
	counts = counts.reshape(-1)
	#sun where is 0
	condition0 = (cluster_labels == 0)
	counts0 = np.ma.masked_where(condition0, counts)
	counts0[counts0.mask] = 0
	sum0 = np.sum(counts0)
	#sum where is 1
	condition1 = (cluster_labels == 1)
	counts1 = np.ma.masked_where(condition1, counts)
	counts1[counts1.mask] = 0
	sum1 = np.sum(counts1)
	
	if sum1>sum0:
		where_rice = (cluster_labels == 1)
	elif sum0>sum1:
		where_rice = (cluster_labels == 0)

	where_rice = np.ma.masked_where(where_rice, unique)
	where_rice[where_rice.mask] = 9999
	a= np.unique(where_rice).tolist()
	a.remove(9999)
	return a

# print (where_rice)
def rice_area(tiff_path, shapefile_path):
	dataset = gdal.Open(tiff_path)
	band = dataset.GetRasterBand(1)
	img = band.ReadAsArray()

	rice_layers = get_rice_layers(tiff_path, shapefile_path)
	conditions = list()
	for layer in rice_layers:
		conditions.append ((img == layer)*1)

	rice = np.sum (np.array(conditions), axis = 0)
	rice_area = np.sum(rice)
	print (rice_area)
	return [rice, rice_area]


# rice_matrix = rice_area(tiff_path, shapefile_path)
# config_this.createTiff(rice_matrix, tiff_path, 'hehe_rice.tif')
# os.remove('yolo.tif')
