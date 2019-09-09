from osgeo import gdal
from osgeo import ogr
import os
import copy
import subprocess
import shutil
import configparser
import connectPostgres

class sen1_name:
    def __init__(self,name):
        self.sat = name.split('_')[0]
        self.orbit = name.split('_')[6]
        self.name = name

        
dirname = os.path.dirname(__file__)
#change file_2 to file_1 and delete file 1.
def change(file_1, file_2):
    os.remove(file_1)
    os.rename(file_2, file_1)

def config (configFile = dirname + '/config/config.txt', section=None):
    parser = configparser.ConfigParser()
    parser.read(configFile)
    return dict(parser.items(section))


def getFoldTiff (folder):
    folders = copy.copy(folder)
    TIFs = []
    allFiles = os.listdir(folders)
    for i in allFiles:
        if '.tif' in i:
            i = folder+'//' + i
            TIFs.append(i)
    return TIFs

#create a Tiff with array, copy metadata of imageDim and path result = outband
def createTiff(arr, imageDim, outband):
    imageDim = gdal.Open(imageDim)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outband,imageDim.RasterXSize,imageDim.RasterYSize,1,6)
    outDs.SetMetadata(imageDim.GetMetadata())
    outDs.SetGeoTransform(imageDim.GetGeoTransform())
    outDs.SetProjection(imageDim.GetProjection())
    outDs.GetRasterBand(1).WriteArray(arr)
    del outDs
#get 1st band from an inRaster
#1VV 2VH
def get1stBand(inRaster):
    raster = gdal.Open(inRaster)
    #1VH 2VV
    band = raster.GetRasterBand(1)
    outRaster = inRaster.replace('.tif','1.tif')
    array = band.ReadAsArray()
    createTiff(array, inRaster, outRaster)
    return outRaster

#clip an raster by shp, inraster = path of raster will be clipped and outraster = path of result
def clip (shp, inRaster, outRaster):
    inRaster2 = get1stBand(inRaster)
    cmdLine2 = "gdalwarp -cutline " +shp + " -crop_to_cutline -of Gtiff -dstnodata 0 -overwrite " + inRaster2 + ' ' + outRaster 
    p1 = subprocess.Popen(cmdLine2,shell=True)
    p1.wait()
    # os.remove(inRaster)
    # os.remove(inRaster2)
    return outRaster

#mosaic all file in a folder and extract result to outfolder
def MosaicFolder (inFolder = None, outFolder = None):
    py = config(section='py_machine')
    py_scripts = py['py_3_scripts']
    alpha = '0'
    inRaster = str()
    Tifs =  getFoldTiff (inFolder)
    print (Tifs)
    for Tif in Tifs:
        inRaster = inRaster + ' ' + Tif                
    outRaster = outFolder + '/' + os.path.basename(inFolder)
    print (inRaster)
    command="py -3 "+py_scripts+"/gdal_merge.py -o "+outRaster+".TIF -of GTiff -ot Float32 -n " + alpha + " -a_nodata NaN"+ inRaster
    p1 = subprocess.Popen(command,shell=True)
    p1.wait()
    return outRaster


def sigma0_dB (inRaster):
    py = config(section='py_machine')
    py_scripts = py['py_3_scripts']
    outRaster = dirname + '/' + inRaster.replace('.TIF','_dB.TIF')
    cmdLine = "py -3 "+py_scripts+"/gdal_calc.py --calc=10*log(A) --type=Float32 --NoDataValue=0 --outfile=%s -A %s"%(outRaster, inRaster)
    p = subprocess.Popen(cmdLine,shell=True)
    p.wait()
    return outRaster

def get_extent (inRaster):
    src = gdal.Open(inRaster)
    ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
    lrx = ulx + (src.RasterXSize * xres)
    lry = uly + (src.RasterYSize * yres)
    return ([ulx, lrx, lry, uly])

