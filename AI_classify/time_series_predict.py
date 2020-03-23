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



def getRasByShape (raster_path, shp_path):
	shapefile = gpd.read_file(shp_path)
	geoms = shapefile.geometry.values
	geometry = geoms[0]
	geoms = [mapping(geoms[0])]
	with rasterio.open(raster_path) as src:
		out_image, out_transform = mask(src, geoms, crop=True)
	return out_image

# get X data from time series in side an raster, then expand to array m*n (m pixels, n dates)
def create_X_data (list_Raster_pth, shp_pth):
	def list_to_tuple(list): 
		return (*list, )
	X = list()
	X = getRasByShape(list_Raster_pth, shp_pth)
	X = X.reshape(X.shape[0],-1)
	X = X.transpose()
	X = np.nan_to_num(X,0)
	bad = np.zeros (X.shape[1])
	# delete all pixel have nan as all feature
	X = np.delete(X, np.argwhere(X == bad), axis = 0)
	return X


infolder = '../../output/X_Y_train/'

file = infolder+'X_train.npy'
X_train = np.load(file)

file = infolder+'Y_train.npy'
Y_train = np.load(file)

file = infolder+'X_test.npy'
X_test = np.load(file)

file = infolder+'Y_test.npy'
Y_test = np.load(file)

validation_data = (X_test, Y_test)

print (X_train.shape)

# create an neural network 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ create batch ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

batch_size = 100

input_dim = X_train.shape[1]
def batch_generator(batch_size, X_data, Y_data):
	"""
	Generator function for creating random batches of training-data.
	"""

	# Infinite loop.
	while True:
		index = np.random.choice(X_data.shape[0], batch_size, replace=False) 
		X_batch = X_data[index]
		Y_batch = Y_data[index]
		yield (X_batch, Y_batch)

X_batch, Y_batch = next(batch_generator(batch_size, X_train, Y_train))

generator = batch_generator(batch_size=batch_size, X_data = X_train, Y_data = Y_train)



model = Sequential()
model.add(Dense(20, input_dim=input_dim, activation='softmax'))
model.add(Dense(10, activation='softmax'))
model.add(Dense(2, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()


path_checkpoint = '24_checkpoint.keras'
callback_checkpoint = ModelCheckpoint(filepath=path_checkpoint, monitor='val_loss', verbose=1, save_weights_only=True)	
callbacks = [callback_checkpoint]
history = model.fit_generator(generator=generator,
                    epochs=100,
                    steps_per_epoch=100,
                    validation_data=validation_data,
                    callbacks=callbacks)

val_loss = history.history['val_loss']
loss 	 = history.history['loss']
plt.plot(val_loss)
plt.plot(loss)
plt.show()