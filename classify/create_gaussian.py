import config_this


def getMatrixBand(inRaster, n):
    raster = gdal.Open(inRaster)
    band = raster.GetRasterBand(int (n))
    outRaster = inRaster.replace('.tif','%s.tif'%(str(n)))
    array = band.ReadAsArray()
    return array


def run (rasters, dates):
	for raster in rasters:
		matrix = getMatrixBand(raster ,1)
		matrix_2 = scipy_ndim.filters.gaussian_filter(matrix, (1,0,0))
	create ()
