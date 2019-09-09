import requests
from osgeo import gdal
from osgeo import ogr
import xml.etree.ElementTree as ET
import os
import configparser
import subprocess
import time
import datetime

dirname = os.path.dirname(__file__)

def config (configFile = dirname + '/config/config.txt', section=None):
    parser = configparser.ConfigParser()
    parser.read(configFile)
    return dict(parser.items(section))

#create a rectangle extent to be embedded to searchURL
def getFootprint(shp):
	driver = ogr.GetDriverByName('ESRI Shapefile')
	dataSource = driver.Open(shp, 0)
	layer = dataSource.GetLayer()
	feature = layer[0]
	geom = feature.GetGeometryRef()
	A = geom.GetEnvelope()
	#(1 4, 2 4, 2 3, 1 3, 1 4) ## (0 3, 1 3, 1 2, 0 2, 0 3)
	footprint = ogr.Geometry(ogr.wkbLinearRing)
	footprint.AddPoint(A[0],A[3])
	footprint.AddPoint(A[1],A[3])
	footprint.AddPoint(A[1],A[2])
	footprint.AddPoint(A[0],A[2])
	footprint.AddPoint(A[0],A[3])
	footprint2 = ogr.Geometry(ogr.wkbPolygon)
	footprint2.AddGeometry(footprint)
	footprint2 = footprint2.ExportToWkt()
	footprint2 = footprint2.replace(' 0,',',')
	return(footprint2)

#create searchURL from platform, sense_date and shapefile
def get_searchURL (platform, sense_date, shp):
	#footprint of input
	footprint = getFootprint(shp)
	#convert to date of corpenicus
	year = int(sense_date[0:4])
	month = int(sense_date[4:6])
	date  = int(sense_date [6:8])
	start_date = datetime.date(year, month, date)
	end_date = start_date + datetime.timedelta(days=150)
	start_date = start_date.strftime("%Y-%m-%d") + 'T00:00:00.000Z'
	end_date = end_date.strftime("%Y-%m-%d") + 'T23:59:59.000Z'

	searchURL = 'https://scihub.copernicus.eu/dhus/search?q=footprint:"Intersects(%s)" AND %s AND beginposition:[%s TO %s]'%(footprint,platform,start_date,end_date)
	print (searchURL)
	return searchURL

#get dictionary of uuid and names of image scenes in case shp intersect with many scenes once
#uuid can be export from page content of searchURL after login and pass URI

def get_uuid_names (page_content):
	root = ET.fromstring(page_content)
	#uuid and name of all intersect
	uuid = list()
	name = list()

	#footprint of out put
	for child1Tag in root.getchildren():
		if 'entry' in child1Tag.tag:
			for child2Tag in child1Tag:
				#find footPrint 
				if 'title' in child2Tag.tag: name.append(child2Tag.text)
				if 'id' in child2Tag.tag: uuid.append(child2Tag.text)
				
	#uuid and name of only footprint = sceneGeom
	uuid2 = list()
	name2 = list()
	for i in range(len(name)):
		if name[i].split('_')[4].split('T')[-1][0:3]== '111':	
			uuid2.append(uuid[i])
			name2.append(name[i])

	uuid_names = dict(zip(uuid2,name2))

	return (uuid_names)

def download(shp, platform, sense_date):
	if not os.path.exists('download'):
		os.mkdir('download')
	else:
		pass
	login_data = config(section='login')
	user = login_data['user']
	password = login_data['password']
	loginURL = login_data['polo']
	searchURL = get_searchURL(platform, sense_date, shp)
	s1 = requests.Session()

	s1.get(searchURL)
	s1.post(searchURL, auth = (user,password))
	page_content = s1.get(searchURL).content
	uuid_names = get_uuid_names(page_content)

	for uuid,name in uuid_names.items():
		s2 = requests.Session()
		s2.get(searchURL)
		s2.post(searchURL, auth = (user,password))
		url = 'https://scihub.copernicus.eu/dhus/odata/v1/Products(\'%s\')/$value'%(uuid)
		local_filename = 'download' + '/' + name + '.zip'
		print ("Downloading %s..."%(local_filename))
		print ("take a cup of coffee! ^^")
		with s2.get(url, stream=True) as r:
			r.raise_for_status()
			with open(local_filename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=8192): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
						f.flush()
	print ('heading to process!!')
	return uuid_names


platform = '(platformname:Sentinel-1 AND producttype:GRD)'
shp = 'D:/python/STAC_intern_project/shp/angiang/angiang.shp'
date = '20181221'
download(shp, platform, date)