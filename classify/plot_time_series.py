import glob
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from osgeo import gdal
from osgeo import ogr


folder = 'D:/python/STAC_intern_project/snappy/rice_Angiang_VV'
rasters = glob.glob("%s/*.TIF"%(folder))
dates = list()
dates2 = list ()
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y%m%d")
    d2 = datetime.strptime(d2, "%Y%m%d")
    return abs((d2 - d1).days)

for raster in rasters:
	date = raster.split('/')[-1].split('_')[-1].split('.')[0]
	dates.append(date)
for date in dates:
	dates2.append(days_between(date, dates[0]))

def showAnimate(root_raster, rasters, dates):

    fig = plt.figure(1)
    imagelist =[]
    for raster in rasters:
        imagelist.append(gdal.Open(raster).ReadAsArray())
        
    root_raster = gdal.Open(root_raster).ReadAsArray()
    masked_array = np.ma.array (imagelist[0], mask=np.isnan(imagelist[0]))

    # #this function will update frame,start 1st frame from 1st element of list
    im = plt.imshow(masked_array,interpolation='nearest',cmap='gray', vmin=0, vmax=1)
    def updatefig(j):
        im.set_array(root_raster)
        return [im]
    ani = animation.FuncAnimation(fig, updatefig, frames=range(len(imagelist)), 
                                  interval=500, blit=True)
    # #create an envent to click and show the plot
    fig2=plt.figure(2)

    def onclick(event):
        plt.figure(2)
        print ('click')
        global ix, iy
        ix, iy= event.xdata, event.ydata
        vals = list()
        for image in imagelist: 
            a = image[int(iy-0.5)][int(ix-0.5)]
            vals.append(a)

        plt.plot(dates,vals)
        plt.gcf().autofmt_xdate()
        # ax = fig.add_subplot(111)
        plt.grid()
        plt.show()
   
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

root_raster = 'D:/python/STAC_intern_project/snappy/rice.TIF'
showAnimate(root_raster,rasters,dates2)