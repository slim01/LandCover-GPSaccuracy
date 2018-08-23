#How to use:
# change sys.path.append to your script path
# adjust (data_dir),gpxFile,elevationRaster,landTypeRasterPath to the correct Paths on your machine
# if the track point layer in your gpx file is called different, adjust trackPointsReprojected
# start script
# make sure your gpx data is not used anywhere before starting the script, otherwise an error will occur


import sys
sys.path.append('C:\\Users\\Sofian\\Documents\\PythonAssignement')
import ogr
import gdal
import os
import osr_transformation
import gpxToShp


def addElevationToShp(EleRast, tpPoints):
    elevation = gdal.Open(EleRast)
    ele_band = elevation.GetRasterBand(1)
    gt=elevation.GetGeoTransform()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(tpPoints, 1)
    layer = dataSource.GetLayer()
    layer.ResetReading()
    field_defn = ogr.FieldDefn("elevation", ogr.OFTString  )    
    layer.CreateField(field_defn)
    field_defn2= ogr.FieldDefn("eleDif", ogr.OFTString  )    
    layer.CreateField(field_defn2)
    for feature in layer:
        geometry = feature.GetGeometryRef()
        xcord = geometry.GetX()
        ycord = geometry.GetY()
        
        px = int((xcord - gt[0]) / gt[1]) #x pixel
        py = int((ycord - gt[3]) / gt[5]) #y pixel
        
        intval=ele_band.ReadAsArray(px,py,1,1)
        val = intval[0]
        strVal = str(val[0])
        eleDif = abs(val[0] - feature.GetField("ele"))
        feature.SetField("elevation", strVal)        
        feature.SetField("eleDif", eleDif)
        layer.SetFeature(feature)
    elevation = None
    dataSource = None
    
def addLandUseTypeToShp(land_raster, tpPoints):
    landTypeRaster = gdal.Open(land_raster)

    if landTypeRaster is None:
        print('Unable to open landTypeRaster')
    else:
        rasterBand =  landTypeRaster.GetRasterBand(1)
        gt=landTypeRaster.GetGeoTransform()
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(tpPoints, 1)
        layer = dataSource.GetLayer()
        layer.ResetReading()
        field_defn = ogr.FieldDefn("landUse", ogr.OFTString)        
        layer.CreateField(field_defn)
        for feature in layer:
            geometry = feature.GetGeometryRef()
            xcord = geometry.GetX()
            ycord = geometry.GetY()
            
            px = int((xcord - gt[0]) / gt[1]) #x pixel
            py = int((ycord - gt[3]) / gt[5]) #y pixel
            
            intval=rasterBand.ReadAsArray(px,py,1,1)
            val = intval[0]            
            strVal = str(val[0])
            feature.SetField("landUse", strVal)
            layer.SetFeature(feature)
        landTypeRaster = None
        dataSource = None
        
    
def calcStatsForLandUseType(tpPoints):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(tpPoints, 1)
    layer = dataSource.GetLayer()
    eleDifsForLandTypes = {}
    for feature in layer:
        eleDif = feature.GetField("eleDif")
        landType = feature.GetField("landUse")
        eleDifsForLandTypes.setdefault(landType, []).append(eleDif)
    print("land cover - avg elevation dif - number of meas") 
    for key, eleDifs in eleDifsForLandTypes.items():
        sum = 0
        for val in eleDifs:
            sum = sum + float(val)
        averageDif = sum / len(eleDifs)
        print(key, averageDif, len(eleDifs))
    
        
        
    
    
data_dir = os.path.join('C:\\', 'Users', 'Sofian', \
'Downloads', 'data')

# Path to gpx file
gpxFile = os.path.join(data_dir, 'Trassentour.gpx')
shapeFromGpx = os.path.join(data_dir, 'shapefiles', \
    'out.shp')

# Path to the raster
elevationRaster = os.path.join(data_dir, 'GermanyDGM1', \
        'dgm1_5meter.img')    
# Path to track points shapefile, change 'track_points.shp' if gpx layer has different name
in_vect = os.path.join(data_dir, 'shapefiles', \
'track_points.shp')

# Path to output shapefile
trackPointsReprojected = os.path.join(data_dir, 'shapefiles', \
                                'track_reprojected.shp')
                                # Path to output shapefile
trackPointsReprojected2 = os.path.join(data_dir, 'shapefiles', \
                                'track_reprojected2.shp')
# Path to landUseType raster 
landTypeRasterPath = os.path.join('C:\\', 'Users', 'Sofian', \
'Downloads', 'data', 'g100_clc12_V18_5.tif')
# (input,output,layerIdOfInput)
gpxToShp.convertToShp(gpxFile,shapeFromGpx,4)
osr_transformation.start_transform(elevationRaster, in_vect, trackPointsReprojected)
addElevationToShp(elevationRaster,trackPointsReprojected)
osr_transformation.start_transform(landTypeRasterPath, trackPointsReprojected, trackPointsReprojected2)
addLandUseTypeToShp(landTypeRasterPath, trackPointsReprojected2)
calcStatsForLandUseType(trackPointsReprojected2)
