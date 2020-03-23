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
import datetime
import config_MCL
from config import config_this
import scipy.ndimage, scipy.signal
from numpy import inf
import predict_data_generate
import data_generate

path_checkpoint = '24_checkpoint.keras'
model = Sequential()
model.add(Dense(20, input_dim=32, activation='softmax'))
model.add(Dense(10, activation='softmax'))
model.add(Dense(2, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()


try:
    model.load_weights(path_checkpoint)
except Exception as error:
    print("Error trying to load checkpoint.")
    print(error)



# time_series_image_pth	= 'C:/Users/longdt/Desktop/Duy/project/rice/sr_code/Time_series_data/20190829_t.tif'
# X, result_shape = predict_data_generate.get_X(time_series_image_pth)

# y_pred = model.predict_classes(X)
# y_pred = y_pred.transpose()

# y_pred = y_pred.reshape(result_shape)
# config_this.createTiff(y_pred, time_series_image_pth, 'a.tif')