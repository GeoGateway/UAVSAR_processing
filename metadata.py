"""
metadata.py
    -- process anns to geojson
    -- update meta data
"""

import os, json
import pandas as pd
import geopandas as gpd

import settings
from anntool import extract_meta

def extract_uid(ann):
    """return uid from ann file name"""
    #uid1540@SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01.ann

    if not "uid" in ann:
        return "0000"
    uid = ann.split("@")[0][3:]

    return uid

def ann2json():
    """ann files to geojson"""

    os.chdir(settings.ANN_DIR)
    anns = [x for x in os.listdir() if x[-4:]=='.ann']
    
    metalist = []
    uidlist = []
    for ann in anns:
        annuid = extract_uid(ann)
        uidlist.append(annuid)
        print(annuid)
        meta_dict = extract_meta(ann)
        meta_dict['UID']= annuid
        metalist.append(meta_dict)
    
    df = pd.DataFrame(metalist)
    #df['geom'] = df['geom'].apply(wkt.loads)
    df['geometry']=gpd.GeoSeries.from_wkt(df['geom'])
    df.drop('geom', axis=1, inplace=True) 

    #df.to_csv('anns.csv')
    gdf = gpd.GeoDataFrame(df,geometry='geometry')
    gdf.crs = 'epsg:4326'

    uidlist.sort()
    metajson = "{}_{}.geojson".format(uidlist[0],uidlist[-1])
    gdf.to_file(metajson, driver='GeoJSON')

    df = None
    gdf = None
    return 

def main():

    ann2json()

if __name__ == "__main__":
    main()