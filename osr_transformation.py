import gdal
import ogr
import os
import osr

def start_transform(in_rast, in_vect, out_fn):

    # Open the raster
    rast_data_source = gdal.Open(in_rast)

    # Get metadata (not required)
    print('nr of bands:', rast_data_source.RasterCount)
    cols = rast_data_source.RasterXSize
    rows = rast_data_source.RasterYSize
    print('extent:', cols, rows)

    # Get georeference info (not required)
    geotransform = rast_data_source.GetGeoTransform()
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    print('cell size:', pixelWidth, pixelHeight)
    originX = geotransform[0]
    originY = geotransform[3]
    print('x, y:', originX, originY)

    rast_spatial_ref = rast_data_source.GetProjection()
    print('raster spatial ref is', rast_spatial_ref)

    # Get the correct driver
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # 0 means read-only. 1 means writeable.
    vect_data_source = driver.Open(in_vect, 0) 

    # Check to see if shapefile is found.
    if vect_data_source is None:
        print('Could not open %s' % (in_vect))

    # Get the Layer class object
    layer = vect_data_source.GetLayer(0)
    # Get reference system info
    vect_spatial_ref = layer.GetSpatialRef()
    print('vector spatial ref is', vect_spatial_ref)

    # create osr object of raster spatial ref info
    sr = osr.SpatialReference(rast_spatial_ref)
    transform = osr.CoordinateTransformation(vect_spatial_ref, sr)

    # Delete if output file already exists
    # We can use the same driver
    if os.path.exists(out_fn):
        print('exists, deleting')
        driver.DeleteDataSource(out_fn)
    out_ds = driver.CreateDataSource(out_fn)
    if out_ds is None:
        print('Could not create %s' % (out_fn))

    # Create the shapefile layer WITH THE SR
    out_lyr = out_ds.CreateLayer('track_points', sr, 
                                 ogr.wkbPoint)

    out_lyr.CreateFields(layer.schema)
    out_defn = out_lyr.GetLayerDefn()
    out_feat = ogr.Feature(out_defn)
    # Loop over all features and change their spatial ref
    for in_feat in layer:
        geom = in_feat.geometry()
        geom.Transform(transform)
        out_feat.SetGeometry(geom)
        # Make sure to also include the attributes in the new file
        for i in range(in_feat.GetFieldCount()):
            value = in_feat.GetField(i)
            out_feat.SetField(i, value)
        out_lyr.CreateFeature(out_feat)

    del out_ds

    print('done')
