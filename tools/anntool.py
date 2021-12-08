
# anntool.py
# parse ann file
# v1, v2
# 

import os, sys
from daynum2k import daynum2k
import pandas as pd
import geopandas as gpd
from shapely import wkt

def ann2dict(ann):
    """ parse ann file to dict object"""
    
    with open(ann,"r") as f:
        lines = f.read()
    f.close

    lines = lines.splitlines()

    V={}
    dataname = os.path.basename(ann).replace(".ann","")
    V['dataname'] = dataname

    for line in lines:
        # no need to parse display parameters
        if  "display parameters" in line:
            break
        # test =
        if "=" in line:
            # there are may more than one =
            pos = line.find("=")
            key, value = line[0:pos],line[pos+1:]
            
            # key, value = line.split("=")[0:2]
            # for key part, need to get rid of (&)
            if "(" in key:
                 a = key.find("(")
                 b = key.find(")")
                 key = key.replace(key[a:b+1],"")
            key = key.strip()
            # for value part, need to get rid of in v2;
            if ";" in value:
                value = value.split(";")[0]
            value = value.strip()
 
            #print key, "=", value
            V[key]=value

    return V

def get_geomfromann(vdict, version):
    """return geom from ann file"""
    
    if version == 1:
        # for version 1 ann, may need to fill the data manually
        #Image Corner 1 Latitude  -> upper left
        #Image Corner 1 Longitude 
        #Image Corner 2 Latitude  -> upper right
        #Image Corner 2 Longitude
        #Image Corner 3 Latitude  -> lower left
        #Image Corner 3 Longitude
        #Image Corner 4 Latitude  -> lower right
        #Image Corner 4 Longitude
        lat0 = float(vdict['Image Corner 1 Latitude'])
        lon0 = float(vdict['Image Corner 1 Longitude'])
        lat1 = float(vdict['Image Corner 2 Latitude'])
        lon1 = float(vdict['Image Corner 2 Longitude'])
        lat2 = float(vdict['Image Corner 4 Latitude'])
        lon2 = float(vdict['Image Corner 4 Longitude'])    
        lat3 = float(vdict['Image Corner 3 Latitude'])
        lon3 = float(vdict['Image Corner 3 Longitude'])

    if version >= 2:
        # suppose it is version 2
        #Approximate Upper Left Latitude
        #Approximate Upper Left Longitude
        #Approximate Upper Right Latitude
        #Approximate Upper Right Longitude
        #Approximate Lower Left Latitude
        #Approximate Lower Left Longitude
        #Approximate Lower Right Latitude
        #Approximate Lower Right Longitude
        lat0 = float(vdict['Approximate Upper Left Latitude'])
        lon0 = float(vdict['Approximate Upper Left Longitude'])
        lat1 = float(vdict['Approximate Upper Right Latitude'])
        lon1 = float(vdict['Approximate Upper Right Longitude'])
        lat2 = float(vdict['Approximate Lower Right Latitude'])
        lon2 = float(vdict['Approximate Lower Right Longitude'])    
        lat3 = float(vdict['Approximate Lower Left Latitude'])
        lon3 = float(vdict['Approximate Lower Left Longitude'])
        
    coords = [[lon0,lat0],[lon1,lat1],[lon2,lat2],[lon3,lat3],[lon0,lat0]]
    #geom = "GeomFromText('POLYGON(("
    geom = "POLYGON(("
    for i in range(len(coords)):
        geom += str(coords[i][0]) + " " + str(coords[i][1])
        geom += ","
    geom = geom[:-1]
    geom += "))"
    #geom += "))', 4326)"
    
    return geom

def extract_meta(annfile):
    """extract meta data from an ann file"""
    
    vdict = ann2dict(annfile)

    dataname = vdict['dataname']

    # find out the version
    if 'UAVSAR RPI Annotation File Version Number' in vdict:
        version = float(vdict['UAVSAR RPI Annotation File Version Number'])
    else:
        version = 1

    # Ground Range Unwrapped Phase
    if (vdict['Ground Range Unwrapped Phase'] == 'N/A' or len(vdict['Ground Range Unwrapped Phase']) <= 10):
        unw = 0
    else:
        unw = 1

    # determine phase sign based on aquisition time order
    if version == 1:
        t1 = vdict['Time of Acquisition for Pass 1'].split()[0]
        t2 = vdict['Time of Acquisition for Pass 2'].split()[0]
    elif version >= 2:
        time1          = vdict['Stop Time of Acquisition for Pass 1']
        time2          = vdict['Stop Time of Acquisition for Pass 2']
        # e.g uid726
        # Start Time of Acquisition for Pass 1           (&)             =  22-Jul-2009 18:18:20 UTC
        # Stop Time of Acquisition for Pass 1            (&)             =  N/A
        # Start Time of Acquisition for Pass 2           (&)             =  29-Sep-2009 18:48:12 UTC
        # Stop Time of Acquisition for Pass 2            (&)             =  N/A
        if time1 == "N/A" or len(time1) < 10:
            time1 = vdict['Start Time of Acquisition for Pass 1']
        if time2 == "N/A" or len(time2) <10:
            time2 = vdict['Start Time of Acquisition for Pass 2']

        t1 = time1.split()[0]
        t2 = time2.split()[0]
    
    tdiff = daynum2k(t1)-daynum2k(t2)
    if tdiff < 0:
        phasesign = -1.0
    else:
        phasesign = 1.0

    if version == 1:
        description    = vdict['Site Description']
        lines          = int(vdict['Ground Range Data Latitude Lines'])
        samples        = int(vdict['Ground Range Data Longitude Samples'])
        startlat       = float(vdict['Ground Range Data Starting Latitude'])
        startlon       = float(vdict['Ground Range Data Starting Longitude'])
        latspace       = float(vdict['Ground Range Data Latitude Spacing'])
        lonspace       = float(vdict['Ground Range Data Longitude Spacing'])
        wavelength     = float(vdict['Center Wavelength'])
        gpsaltitude    = float(vdict['Average GPS Altitude'])
        terrainheight  = float(vdict['Average Terrain Height'])
        peglat         = float(vdict['Peg Latitude'])
        peglon         = float(vdict['Peg Longitude'])
        peghead        = float(vdict['Peg Heading'])
        radardirection = vdict['Radar Look Direction']
        time1          = vdict['Time of Acquisition for Pass 1']
        time2          = vdict['Time of Acquisition for Pass 2']
        url            = vdict['URL']
    elif version >= 2:
        description    = vdict['Site Description']
        lines          = int(vdict['Ground Range Data Latitude Lines'])
        samples        = int(vdict['Ground Range Data Longitude Samples'])
        startlat       = float(vdict['Ground Range Data Starting Latitude'])
        startlon       = float(vdict['Ground Range Data Starting Longitude'])
        latspace       = float(vdict['Ground Range Data Latitude Spacing'])
        lonspace       = float(vdict['Ground Range Data Longitude Spacing'])
        wavelength     = float(vdict['Center Wavelength'])
        gpsaltitude    = float(vdict['Global Average Altitude'])
        terrainheight  = float(vdict['Global Average Terrain Height'])
        peglat         = float(vdict['Peg Latitude'])
        peglon         = float(vdict['Peg Longitude'])
        peghead        = float(vdict['Peg Heading'])
        radardirection = vdict['Radar Look Direction']
        time1          = vdict['Stop Time of Acquisition for Pass 1']
        time2          = vdict['Stop Time of Acquisition for Pass 2']
        # e.g uid726
        # Start Time of Acquisition for Pass 1           (&)             =  22-Jul-2009 18:18:20 UTC
        # Stop Time of Acquisition for Pass 1            (&)             =  N/A
        # Start Time of Acquisition for Pass 2           (&)             =  29-Sep-2009 18:48:12 UTC
        # Stop Time of Acquisition for Pass 2            (&)             =  N/A
        if time1 == "N/A" or len(time1) < 10:
            time1 = vdict['Start Time of Acquisition for Pass 1']
        if time2 == "N/A" or len(time2) <10:
            time2 = vdict['Start Time of Acquisition for Pass 2']

        url            = vdict['URL']

    # get geom
    if version >= 2:
        geom = get_geomfromann(vdict,version)
    else:
        geom = ''

    # dataname,description,lines,samples,startlat,startlon,latspace,lonspace,wavelength,gpsaltitude,terrainheight,peglat,peglon,peghead,radardirection,time1,time2,phasesign,version,url,geom
    meta = {}
    meta['dataname']=dataname
    meta['description']=description
    meta['lines']=lines
    meta['samples']=samples
    meta['startlat']=startlat
    meta['startlon']=startlon
    meta['latspace']=latspace
    meta['lonspace']=lonspace
    meta['wavelength']=wavelength
    meta['gpslatitude']=gpsaltitude
    meta['terrainheight']=terrainheight
    meta['peglat']=peglat
    meta['peglon']=peglon
    meta['peghead']=peghead
    meta['radardirection']=radardirection
    meta['time1']=time1
    meta['time2']=time2
    meta['phasesign']=phasesign
    meta['version']=version
    meta['url']=url
    meta['unw'] = unw
    meta['geom']=geom
    
    return meta

def debug():

    # parse v1 ann file
    ann = "v1.ann"
    #v = ann2dict(ann)
    v = extract_meta(ann)
    print(v)
    # parse v2 ann file
    ann = "v2.ann"
    #v = ann2dict(ann)
    v = extract_meta(ann)
    print(v)

def main():
    """ scan a whole folder """ 

    annfolder = 'ann'
    annlist = [ x for x in os.listdir(annfolder) if x[-4:]=='.ann']
    metalist = []
    for annfile in annlist:
        meta_dict = extract_meta(annfolder + os.path.sep + annfile)
        metalist.append(meta_dict)
    
    df = pd.DataFrame(metalist)
    #df['geom'] = df['geom'].apply(wkt.loads)
    df['geometry']=gpd.GeoSeries.from_wkt(df['geom'])
    df.drop('geom', axis=1, inplace=True) 
    print(df.head())
    #df.to_csv('anns.csv')
    gdf = gpd.GeoDataFrame(df,geometry='geometry')
    gdf.crs = 'epsg:4326'
    print(gdf.head())
    gdf.to_file("anns.geojson", driver='GeoJSON')

if __name__ == "__main__":
    #debug()
    main()

