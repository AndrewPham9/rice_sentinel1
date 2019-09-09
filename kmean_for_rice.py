from sklearn import cluster
from osgeo import gdal
import numpy as np
import kmean_for_polygon
import config_this

shapefile_path = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/angiang/train/trained_rice.shp'


#create a rice_matrix with metadata from imageDim and 2d std array from  arr, finally name outband
def rice_image(arr, imageDim, outband, k):
	shape1 = arr.shape
	X = arr.reshape((-1, 1))
	X = np.nan_to_num(X)

	kmeans_cluster = cluster.KMeans(n_clusters=k, max_iter = 15)
	kmeans_cluster.fit(X)
	cluster_centers = kmeans_cluster.cluster_centers_
	cluster_labels = kmeans_cluster.labels_

	config_this.createTiff(cluster_labels.reshape(shape1), imageDim, 'buffer_%s.tif'%(k))
	rice_image = kmean_for_polygon.rice_area('buffer_%s.tif'%(k), shapefile_path)[0]
	config_this.createTiff(rice_image, imageDim, outband)
	return rice_image[1]



