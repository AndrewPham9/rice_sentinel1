import os
import subprocess
import shutil
import glob
from datetime import datetime
import sys

sys.path.insert(1, '../')
from config import config_this

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
	gpt = con['gpt']

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

fold = 'D:/python/STAC_intern_project/Download-and-process-sentinel1-rice/rice_anGiang'
for i in range(7):
	if i == 0:
		pass
	else:
		output =  os.path.basename(config_this.getFoldTiff(fold)[30+i]).split('.')[0].split('_')[4] + '.tif'
		processByXML (config_this.getFoldTiff(fold)[i:30+i], output)

