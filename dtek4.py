import requests
import urllib.request as urllib2
import argparse
import sys
import math
from osgeo import gdal
from osgeo import ogr
from gdalconst import*
import os
import re
import copy
import shutil
import zipfile
import downSen
import pre_process
import connectPostgres
import glob
import stacking
import potential_rice

def run(shp,date,province):
	#create rice_folder of this province to store final result (after mosaic)
	dir_path = os.path.dirname(os.path.realpath(__file__))
	mother_folder = 'rice_%s'%(province)
	if not os.path.exists(mother_folder):
		os.mkdir(mother_folder)
	else:
		pass
	all_zips = list()
	platform = '(platformname:Sentinel-1 AND producttype:GRD)'
	uuid_names = downSen.download(shp, platform, date)
	for uuid,name in uuid_names.items():
		all_zips.append('download' + name + '.zip')

	# data_folder = 'D:/python/STAC_intern_project/snappy/data'
	# all_zips = os.listdir(data_folder)

	### => have a list of zips (all_zip)
	for sen_zip in all_zips:
		sen_folder = sen_zip.split('.')[0]
		date = sen_zip.split('_')[4].split('T')[0]
		
		#create a sen_folder to extract zip
		if not os.path.exists(sen_folder):
			os.mkdir(sen_folder)
		else:
			pass

		path_to_zip = data_folder + '/' +sen_zip
		with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
			print ('unzipping...')
			zip_ref.extractall(sen_folder)
		result = pre_process.processByXML(sen_folder, shp, province,'rice_%s_%s'%(province, date))
		new_raster = dir_path.replace('\\','/') + '/' + mother_folder + '/' + os.path.basename(result)
		shutil.move(result, new_raster)

		# write a record to postgreSQL
		fieldsValues ={
		'path' : "'%s'"%(new_raster),
		'date' : '''TO_DATE('%s', 'YYYYMMDD')'''%(date),
		}
		connectPostgres.insertSQL('date_sigma0',**fieldsValues)
	# stack all raster from 7 months
	stacking_rasters = connectPostgres.select_since_6months('date_sigma0', '%s'%(date))
	stacking.processByXML(stacking_rasters, 'stacked_multiTemporalFilter_rice_%s'%(date))
	# potential_rice.rice_potential ('stacked_multiTemporalFilter_rice_%s'%(date)+'.tif', -13, -17)
def main ():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", dest = "shp" , help = "put lowLeftLong here", type = str)
	parser.add_argument("-d", dest = "date" ,help = "put lowLeftLat here", type = str)
	parser.add_argument("-p", dest = "province" ,help = "put upRightLong here", type = str)

	args = parser.parse_args()
	

	# result = run(args.shp,args.date,args.province)
	shp = 'D:/python/STAC_intern_project/shp/angiang/angiang.shp'
	date = '20190811'
	province = 'anGiang'
	result = run (shp, date, province)

if __name__=='__main__':
	main()  

