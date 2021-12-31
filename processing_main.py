"""
processing_main.py
    -- the main script to processing a RPI product
    -- download and covert unw.grd and hgt.grd to geotiff
    -- download overview kml
    -- generate thumbnail.tiff
    -- update metadata
    -- generate alternative coloring 
"""

prolog="""
**PROGRAM**
    processing_main.py
      
**PURPOSE**
    Processing a RPI product
**USAGE**
"""
epilog="""
**EXAMPLE**
    processing_main.py 
               
"""

import os
import sys
import argparse
import logging
import subprocess
import shutil

import settings

from utilities import create_path
from downloadkml import overview_kml

def download_data(dataname,downloadir,jplpath=False):
    """ download data from alaska"""

    # remove HH or VV from dataname
    foldername = dataname.replace("HH","")
    foldername = foldername.replace("VV","")

    if jplpath:
        #http://downloaduav.jpl.nasa.gov/Release2d/JapanV_34901_12094-002_13173-003_0402d_s01_L090_02/JapanV_34901_12094-002_13173-003_0402d_s01_L090HH_02.amp2.grd
        baseurl = os.path.join("http://downloaduav.jpl.nasa.gov/",jplpath,foldername)
    else:
        baseurl = os.path.join("http://uavsar.asfdaac.alaska.edu/", "UA_" + foldername)
    
    filelist ={"ann":".ann", "hgt":".hgt.grd","unw":".unw.grd","unwkmz":".unw.kmz"}
    
    for filetype in filelist.keys():
        downfile = dataname + filelist[filetype]
        logging.info("downloading: {}".format(downfile))

        if os.path.exists(downfile):
            logging.info("skip: {}".format(downfile))
            continue
        aurl = os.path.join(baseurl,downfile)
        # guide: https://urs.earthdata.nasa.gov/documentation/for_users/data_access/curl_and_wget
        # wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies http://server/path
        wgetcmd = "wget -nc --load-cookie ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies {}".format(aurl)
        
        exitcode = subprocess.call(wgetcmd, shell=True)
        if not exitcode == 0:
            #something wrong with downloading
            logging.error("download failed: {}".format(aurl))
            sys.exit()
    return

def generate_header(ann):
    """generate header from ann file"""

    with open(ann,'r') as f:
        lines = f.readlines()

    # v1.ann
    # find the following numbers
    # Ground Range Data Latitude Lines               (-)             =  5895
    # Ground Range Data Longitude Samples            (-)             =  12683
    # Ground Range Data Starting Latitude            (deg)           =  33.02203044
    # Ground Range Data Starting Longitude           (deg)           =  -115.75075932
    # Ground Range Data Latitude Spacing             (deg)           =  -0.000055560
    # Ground Range Data Longitude Spacing            (deg)           =  0.000055560
    
    # v2.ann
    # Ground Range Data Latitude Lines               (-)             =  7779
    # Ground Range Data Longitude Samples            (-)             =  14181
    # Ground Range Data Starting Latitude            (deg)           =  47.43229428           ; center of upper left ground range pixel
    # Ground Range Data Starting Longitude           (deg)           =  -122.17849572         ; center of upper left ground range pixel
    # Ground Range Data Latitude Spacing             (deg)           =  -0.00005556
    # Ground Range Data Longitude Spacing            (deg)           =  0.00005556

    keystr = "Ground Range Data"

    values=[]
    for line in lines:    
        if line[:len(keystr)] == keystr: 
            print(line)
            # for v2. get rid of ;
            if ";" in line:
                # pick up the first part
                line = line.split(";")[0]
            value = float(line.split("=")[1])
            values.append(value)
    print(ann)
    print(values)
    if len(values) != 6:
        logging.error("generate header failed: {}".format(ann))
        logging.error(values)
        sys.exit()

    height = int(values[0])
    width  = int(values[1])
    startlat = values[2]
    startlon = values[3]
    latspace = values[4]
    lonspace = values[5]
    
    # reference: http://www.roipac.org/Viewing_results
    # lower left (LL) corner :  Y_FIRST + (Y_STEP*YMAX)
    # NCOLS 20521
    # NROWS 6306
    # XLLCORNER -116.08600836
    # YLLCORNER 32.5814
    # CELLSIZE 0.000055560
    # NODATA_VALUE 0.0
    # BYTEORDER LSBFIRST

    hdr  = "NCOLS " + str(width) + "\n"
    hdr += "NROWS "  + str(height) + "\n"
    hdr += "XLLCORNER " + str(startlon) + "\n"
    hdr += "YLLCORNER " + str(startlat + height * latspace) + "\n"
    hdr += "CELLSIZE " + "%.9f" % abs(lonspace) + "\n"
    # nodata value may be different 
    #hdr += "NODATA_VALUE " + "0.0" + "\n"
    hdr += "PIXELTYPE FLOAT" + "\n"
    hdr += "BYTEORDER LSBFIRST" + "\n"
    
    # save hdr files 
    image = ann[:-4]
    
    # ground files: int.grd, unw.grd, cor.grd,amp1.grd,amp2.grd,hgt.grd
    #datafiles= ["los.grd", "unw.grd", "cor.grd","amp1.grd","amp2.grd","hgt.grd"]
    datafiles= ["unw.grd", "hgt.grd"]
    
    for name in datafiles:
        if name != "hgt.grd":
            hdrfinal = hdr + "NODATA_VALUE " + "0.0" + "\n"
        else:
            hdrfinal = hdr + "NODATA_VALUE " + "-10000" + "\n"
        hdrname = image + "." + name[:-4] + ".hdr"
        with open (hdrname, "w") as f:
            f.write(hdrfinal)
            f.write('\n')

    return


def grd2tiff(uid,dataname):
    """convert grd file to geotiff"""
   
    # assume it is in the processing folder
    # check outpout folder
    output_dir = os.path.join(settings.PRODUCT_DIR,"uid_" + uid)
    create_path(output_dir)

    # generate header first
    ann = dataname + ".ann"
    generate_header(ann)

    # run geotiff coversion 
    # for large file using compression
    grds = ["unw.grd", "hgt.grd"]
    compress_method = {"unw.grd":"PACKBITS","hgt.grd":"DEFLATE"}

    for grd in grds:
        grdsource = ".".join([dataname,grd])

        try:
            grdsize = os.path.getsize(grdsource)
        except OSError:
            logging.error("failed on getsize: {}".format(grdsource))

        grdsize = grdsize / (1024.0*1024.0*1024.0) # in Gb
        large_file_flag = False
        if grdsize > 3.2:
            large_file_flag = True

        # tiff is uid1234_unw.tiff
        outputtiff = "uid{}_{}.tiff".format(uid,grd[:-4])
        if large_file_flag:
            gdalcmd = "gdal_translate -a_srs EPSG:4326 -co TILED=YES -co COMPRESS={} -of GTiff {} {}".format(compress_method[grd], grdsource, outputtiff)
        else:
            gdalcmd = "gdal_translate -a_srs EPSG:4326 -co TILED=YES -of GTiff {} {}".format(grdsource, outputtiff)
        
        exitcode = subprocess.call(gdalcmd, shell=True)
        if not exitcode == 0:
            #something wrong with downloading
            logging.error("tiff conversion failed: {}".format(grdsource))
            sys.exit()
        # run build overview
        gdalcmd = "gdaladdo -r average {} 2 4 8 16 32".format(outputtiff)
        exitcode = subprocess.call(gdalcmd, shell=True)

        # mv generated tiffs to output_dir
        # copy .hdr and .ann to targetuiddir
        cmd = "mv {} {}".format(outputtiff, output_dir)
        os.system(cmd)
        logging.info("tiff created: {}".format(outputtiff))

    # copy ann to outout_dir
    cmd = "cp *.ann {}".format(output_dir)
    os.system(cmd)

    return

def processing_joblist(joblist,jpl=False,skipdownload=False):
    """ processing list of UAVSAR data"""

    print(joblist)

    if not os.path.exists(joblist):
        print("not found: ",joblist)
        sys.exit()
    
    jobname = os.path.basename(joblist)
    logfile = jobname + ".log"
    # per job log
    logfile = os.path.join(settings.LOG_DIR,logfile)
    logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO)

    # expectet format:
    # uid,dataname
    # for jpl
    # uid,dataname,jplfolder
    # uid,dataname,alaska

    with open(joblist,"r") as f:
        lines = f.readlines()
    
    for entry in lines:
        entry = entry.strip()
        if jpl:
            # 366,SanAnd_05512_10058-002_10077-008_0112d_s01_L090HH_01,Release2e
            uid,dataname, jplpath = entry.split(",")
        else:
            uid,dataname = entry.split(",")[:2]
        
        download_dir = os.path.join(settings.WORKING_DIR,"uid_" + str(uid))

        create_path(download_dir)
        
        # switch download_dir for processing
        os.chdir(download_dir)
        logging.info("processing {} - {}".format(uid,dataname))

        # download data
        if not skipdownload:
            if jpl:
                download_data(dataname,download_dir,jplpath = jplpath)
            else:
                download_data(dataname,download_dir)
        
        #convert 2 geotiff
        #grd2tiff(uid,dataname)

        # processing overview kml
        #overview_kml(uid,dataname)

        # copy ann file to ann folder
        newann = "uid{}@{}.ann".format(uid,dataname)
        newann = os.path.join(settings.ANN_DIR,newann)
        cmd = "cp {}.ann {}".format(dataname,newann)
        #os.system(cmd)

        # copy unw.kmz to highres folder
        newkmz = "uid{}@{}.unw.kmz".format(uid,dataname)
        newkmz = os.path.join(settings.HIGHRES_DIR,newkmz)
        cmd = "mv {}.unw.kmz {}".format(dataname,newkmz)
        #os.system(cmd)

        # zip the folder
        os.chdir(settings.WORKING_DIR)
        zipped = "uid_{}.zip".format(uid)
        zipcmd = "zip -r {} uid_{}/*".format(zipped,uid)
        os.system(zipcmd)

        # then delete the folder
        pfolder = "uid_" + uid
        try:
            shutil.rmtree(pfolder)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        
        # switch back for safety
        os.chdir(settings.BASE_DIR)

def _getParser():
    parser = argparse.ArgumentParser(description=prolog,epilog=epilog,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-j', '--job', action='store', dest='joblist',required=True,help='list of RPI products')
    parser.add_argument('--jpl', default=False, action='store_true', dest='jpl',required=False,help='download data from JPL folder')
    parser.add_argument('--skipdownload', default=False, action='store_true', dest='skipdownload',required=False,help='skip download')
   

    return parser

def main():
    
    parser = _getParser()
    results = parser.parse_args()
    
    if results.jpl:
        processing_joblist(results.joblist, jpl=True,skipdownload=results.skipdownload)
    else:
        processing_joblist(results.joblist,jpl=False,skipdownload=results.skipdownload)

if __name__ == "__main__":
    main()
