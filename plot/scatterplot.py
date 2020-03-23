from osgeo import gdal
import geopandas as gpd
from shapely.geometry import mapping
import rasterio
from rasterio.mask import mask
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  
import matplotlib.pyplot as plt

def getRasByShape (raster_path, shp_path):
    shapefile = gpd.read_file(shp_path)
    geoms = shapefile.geometry.values
    geometry = geoms[0]
    geoms = [mapping(geoms[0])]
    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, geoms, crop=True)
    return out_image


def create_X_train (rast_pth1, rast_pth2, rast_pth3, shp_pth):
    #1,2,3 tif is 3 feature_space for rice
    X1 = getRasByShape(rast_pth1, shp_pth).reshape((-1, 1))
    X2 = getRasByShape(rast_pth2, shp_pth).reshape((-1, 1))
    X3 = getRasByShape(rast_pth3, shp_pth).reshape((-1, 1))
    X1, X2, X3 = np.nan_to_num(X1,0), np.nan_to_num(X2, 0), np.nan_to_num(X3, 0)

    X = np.concatenate((X1,X2,X3), axis=1)
    X = np.delete(X, np.argwhere(X == [0,0,0]), axis = 0)
    return X

r1  = 'output3/1.tif'
r2  = 'output3/2.tif'
r3  = 'output3/3.tif'

rice = 'output3/train_rice.shp'
norice = 'input/train_shapefile/trained_norice_4326.shp'

a1 = create_X_train(r1,r2,r3,rice)
a2 = create_X_train(r1,r2,r3,norice)
# print (a1[:,0].shape)

np.random.shuffle(a1)
a1 = a1[0:500,:]
fig = plt.figure()
ax = fig.add_subplot(111)#, projection='3d')
# a11 = (a1[:,0]-np.nanmin(a1[:,0]))/(np.nanmax(a1[:,0])-np.nanmin(a1[:,0]))
# a12 = (a1[:,1]-np.nanmin(a1[:,1]))/(np.nanmax(a1[:,1])-np.nanmin(a1[:,1]))
# a13 = (a1[:,2]-np.nanmin(a1[:,2]))/(np.nanmax(a1[:,2])-np.nanmin(a1[:,2]))

# ax.scatter(a11,a12,a13,alpha=1)

ax.scatter(a1[:,0],a1[:,2],alpha=0.5,color='b',label='rice')

np.random.shuffle(a2)
a2 = a2[0:500,:]
# a21 = (a2[:,0]-np.nanmin(a2[:,0]))/(np.nanmax(a2[:,0])-np.nanmin(a2[:,0]))
# a22 = (a2[:,1]-np.nanmin(a2[:,1]))/(np.nanmax(a2[:,1])-np.nanmin(a2[:,1]))
# a23 = (a2[:,2]-np.nanmin(a2[:,2]))/(np.nanmax(a2[:,2])-np.nanmin(a2[:,2]))
# ax.scatter(a21,a22,a23,alpha=1)
ax.scatter(a2[:,0],a2[:,2],alpha=0.5,color='r',label='no rice')
ax.set_xlabel('std',size = 20)
ax.set_ylabel('b', size = 20)
# ax.set_zlabel('b')
ax.legend()
plt.show()