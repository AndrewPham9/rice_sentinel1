from osgeo import gdal
from osgeo import ogr
import subprocess
import os
from glob import glob
import configparser
import shutil
import config_this


def processByXML (infolder, shp ,province, outfolder):
	##config all
	con = config_this.config(section='config')
	wget, gpt, sen2cor = con['wget'], con['gpt'], con['sen2cor']

	processDataset = config_this.config(section='processDataset')
	bat, XML, properties1, properties2= processDataset['bat'], processDataset['xml'], processDataset['properties1'],  processDataset['properties2']


	#put sourceproduct_2 as inraster
	sourceproduct_1 = infolder + '/' + os.listdir(infolder)[0]
	outRaster = sourceproduct_1.replace('.SAFE','')

	# insert geometry of shape file to cutline in SNAP
	driver = ogr.GetDriverByName("ESRI Shapefile")	
	data = driver.Open(shp, 0)
	layer = data.GetLayer()
	for feature in layer:
		geom = feature.GetGeometryRef()

	with open(properties1, 'r') as f1:
		with open (properties2, 'w') as f2:
			lines = f1.readlines()
			for line in lines:
				if line.startswith('theGeom'):
					lines[lines.index(line)] = line.replace('hahatheGeomhaha',str(geom))
					f2.writelines(lines)

	# reprocessing
	cmdLine = "%s %s -p %s -SsourceProduct=%s -t %s -f %s"%(gpt,XML,properties2,sourceproduct_1,outRaster,'GeotifF')
	print (cmdLine)
	p1 = subprocess.Popen(cmdLine,shell=True)
	p1.wait()
	
	return outRaster + '.tif'
	os.remove(properties2)
	# shutil.rmtree(infolder)


