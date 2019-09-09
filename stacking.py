import os
import subprocess
import shutil
import glob
from datetime import datetime
import config_this


infolder = 'D:/python/STAC_intern_project/snappy/rice_sentinel1_test/No_clip/rice_test'
inRasters = glob.glob(infolder + '/*.tif')
inRasters2 = list()
for inRaster in inRasters:
	inRasters2.append(inRaster.replace('\\','/'))

#write list TIff as SNAP format with list inRaster to properies_1
def write_properties(inRasters, properties_1):
	properties_files = str()
	for inRasters in inRasters:
		properties_files = properties_files  + inRasters + ','
	properties_files = ('files='+properties_files)[0:-1]
	with open(properties_1, 'w') as f:
		f.write(properties_files)

def processByXML (inRasters, outRaster):
	##config all
	con = config_this.config(section='config')
	wget, gpt, sen2cor = con['wget'], con['gpt'], con['sen2cor']

	processDataset = config_this.config(section='filterDataset')
	XML, properties1= processDataset['filter_xml'], processDataset['filterxml_properties1']

	write_properties(inRasters, properties1)

	# put sourceproduct_2 as inraster
	# insert geometry of shape file to cutline in SNAP
	# reprocessing
	
	cmdLine = "%s %s -p %s -t %s -f %s"%(gpt,XML,properties1,outRaster,'GeotifF')
	print (cmdLine)
	p1 = subprocess.Popen(cmdLine,shell=True)
	p1.wait()


