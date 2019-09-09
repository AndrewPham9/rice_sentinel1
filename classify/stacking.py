import os
import subprocess
import shutil
import glob
from datetime import datetime

from osgeo import gdal

infolder = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/rice_test/'
output = 'hehe.vrt'

# run buildvrt will conflict with from osgeo import gdal
# stacking all image in folder arcording to alphabet and return path of output

def classify (inRaster, dates):
	three_D_val = list()
	raster = gdal.Open(inRaster)
	for i in range (raster.RasterCount):
		band = raster.GetRasterBand(i+1)
		array_val = band.ReadAsArray()
		three_D_val.append(array_val)

	three_D_val = tuple(three_D_val)
	three_D_val = np.stack(three_D_val,axis = 0)
	print (three_D_val)
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y%m%d")
    d2 = datetime.strptime(d2, "%Y%m%d")
    return abs((d2 - d1).days)

def get_date (infolder):
	dates = list()
	three_D_date = list()
	inRasters = glob.glob(infolder + '/*.tif')
	for inRaster in inRasters:
		dates.append(os.path.basename(inRaster).split('_')[2].split('.')[0])
	for date in dates:
		three_D_date.append(days_between(str(date),str(dates[0])))
	return (three_D_date)

def stack_folder (infolder, output):

	inRasters = glob.glob(infolder + '/*.tif')
	gdal.BuildVRT(output, inRasters, separate  = True, resampleAlg = 'nearest')
	output2 = output.replace('.vrt','.tif')
	cmd2 = 'gdal_translate %s %s'%(output, output2)
	p2 = subprocess.Popen(cmd2)
	p2.wait()
	dates = get_date(infolder)
	return [output2, dates]
	
print (stack_folder (infolder, output))
