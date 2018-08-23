import os
import ogr

#############
def convertToShp(in_path, out_file, layerId):
    driver = ogr.GetDriverByName('GPX')

    # 0 means read-only. 1 means writeable.
    data_source = driver.Open(in_path, 0) 
    print(data_source)

    # Check to see if shapefile is found.
    if data_source is None:
        print('Could not open %s' % (in_path))
    else:
        print('Opened %s' % (in_path))
        layer = data_source.GetLayer(layerId)
        featureCount = layer.GetFeatureCount()
        print("Number of features in %s: %d" % \
              (os.path.basename(in_path),featureCount))

    if os.path.exists(out_file):
        print('exists, deleting')
        driver.DeleteDataSource(out_file)

    out_ds  = ogr.GetDriverByName('ESRI Shapefile').\
    CopyDataSource(data_source, out_file)
    del data_source
    del out_ds

