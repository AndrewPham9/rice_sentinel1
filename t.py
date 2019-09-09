import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as scipy_ndim
from osgeo import gdal
from osgeo import ogr
import os
import numpy as np

a = np.array([[1,2,3,4,5],[3,4,6,1,8]])
print (a)
print (a.shape)
b =  (a[:,0:2])
print (b.shape)