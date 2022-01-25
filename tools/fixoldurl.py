"""fixoldurl.py
    -- set url for the old data set
    -- https://github.com/GeoGateway/UAVSAR_processing/issues/13
"""

import os, sys
import geopandas as gpd

def updateurl(url,dataname):
    """updateurl"""

    newurl = url
    if not url == None:
        return url

    
    return newurl

metadata = "1538.geojson"
fixedmeta = "1538_url_fix.geojson"

sdata = gpd.read_file(metadata)
sdata.set_index("UID",inplace=True,drop=False)

sdata['URL']=sdata.apply(lambda x: updateurl(x['URL'],x['Dataname']), axis=1)

print(sdata['URL'])