import glob
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from osgeo import gdal
from osgeo import ogr
import sys
import matplotlib as mpl
import scipy.ndimage


def plot(background_raster, raster):
	fig = plt.figure(1)	
	background = gdal.Open(background_raster).ReadAsArray()

	masked_array = np.ma.array (background, mask=(background==-9999))
	cmap = matplotlib.cm.jet
	cmap.set_bad('white',1.)
	plt.imshow(masked_array, interpolation='nearest', cmap=cmap)

	# plt.imshow(background,cmap='gray', vmin=0, vmax=1)

	sigma = gdal.Open(raster).ReadAsArray()
	dB = 10*np.log10(sigma)
	dB = scipy.ndimage.gaussian_filter(dB, order = 0, sigma = 1.5)

	def onclick(event):
		print('press', event.key)
		sys.stdout.flush()
		def plot_event(alpha):
			fig2 = plt.figure(2)
			print ('click')
			global ix, iy
			ix, iy= event.xdata, event.ydata
			vals = list()
			x = int(ix-0.5)
			y = int(iy-0.5)
			plot_with_xy(dB, x, y,alpha)
			plt.legend()
			plt.gca().set_ylim([-35, -10])
			plt.grid()
			plt.show()


		if event.key == '1':
			plot_event (1)
		if event.key == '2':
			plot_event (2)
		if event.key == '3':
			plot_event (3)
		if event.key == '4':
			plot_event (4)
		if event.key == '0':
			plot_event (0)

	cid = fig.canvas.mpl_connect('key_press_event', onclick)
	plt.show()


def plot_with_xy (matrix,x,y,alpha):
	print (alpha)
	color = ['r', 'g', 'b', 'yellow', 'purple']
	a = color[alpha]
	dB_sorted = matrix

	val = dB_sorted[:,y,x]
	X = np.arange(0,len(val),1)
	plt.plot (X, val, a)


raster = 'C:/Users/longdt/Desktop/Duy/project/rice/sr_code/Time_series_data/35.tif'
background_raster = 'C:/Users/longdt/Desktop/Duy/project/rice/sr_code/output/final_structure.tif'
plot(background_raster,raster)