"""
processing_main.py
    -- the main script to processing a RPI product
    -- download and covert unw.grd and hgt.grd to geotiff
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
import settings

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
        wgetcmd = "wget --load-cookie ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies {}".format(aurl)
        
        exitcode = subprocess.call(wgetcmd, shell=True)
        if not exitcode == 0:
            #something wrong with downloading
            logging.error("download failed: {}".format(aurl))
            sys.exit()
    return

def processing_joblist(joblist,jpl=False,skipdownload=False):
    """ processing list of UAVSAR data"""

    print(joblist)
    print(jpl)

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
        lines = f.read()
    f.close()

    lines = lines.split()
    
    for entry in lines:
        if jpl:
            # 366,SanAnd_05512_10058-002_10077-008_0112d_s01_L090HH_01,Release2e
            uid,dataname, jplpath = entry.split(",")
        else:
            uid,dataname = entry.split(",")[:2]
        
        download_dir = os.path.join(settings.WORKING_DIR,"uid_" + str(uid))

        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        
        # switch download_dir for processing
        os.chdir(download_dir)
        logging.info("processing {} - {}".format(uid,dataname))

        if not skipdownload:
            if jpl:
                download_data(dataname,download_dir,jplpath = jplpath)
            else:
                download_data(dataname,download_dir)
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
