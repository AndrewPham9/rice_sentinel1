
import datetime
from datetime import timedelta
# from pre_processing import stacking


class pth:
    def __init__(self, pth):
        self.date = datetime.datetime.strptime(pth.split('/')[-1].split('.')[0].split('T')[0], '%Y%m%d')
    def __str__(self):
        return str(self.date.strftime("%Y%m%d"))

def insert_interpolating_tif(many_pths, i):
	# get the day which the day before is missing. subtract 6 day to find missng date
	a = pth(many_pths[i])
	missing_date = a.date - timedelta(days = 6)
	missing_date = str(missing_date.strftime("%Y%m%d"))
	# then get missing pth
	missing_pth  = many_pths[i].replace(a.date.strftime("%Y%m%d"), missing_date)
	# pop the first date out of list
	many_pths.pop(0)
	# stack 59 date
	pth = stacking.processByXML(many_pths, 'buffer_for_missing_image.tif')
	# to find missing date by the average of 59 date
	array = gdal.Open('buffer_for_missing_image.tif').ReadAsArray()
	array = numpy.average(array, axis=0)
	# and write into an 
	config_this.createTiff(array,'buffer_for_missing_image.tif', missing_pth)
	os.remove('buffer_for_missing_image.tif')
	pass 
def check_path (many_pths):
	for i in range(len(many_pths)):
		if i == 0: pass
		else:
			delta = (pth(many_pths[i]).date-pth(many_pths[i-1]).date).days
			if delta == 6: pass
			else:
				insert_interpolating_tif(many_pths, i)





pth1 = 'a/20181220T224427.tif'
pth2 = 'a/20181226T224427.tif'
pth3 = 'a/20190101T224427.tif'
pth4 = 'a/20190114T224427.tif'
pths = [pth1, pth2, pth3, pth4]

check_path(pths)