"""
downloadkml.py
    -- download overview kml
    -- fix kml
"""
import os
import settings

from utilities import create_path

def overview_kml(uid, dataname):
    """download kml"""

    # kml/uid1540
    kmlfolder = os.path.join(settings.KML_DIR, "uid"+uid)
    create_path(kmlfolder)
    os.chdir(kmlfolder)
       
    baseurl = "http://uavsar.jpl.nasa.gov/kml/RPI/"
    
    filelist = {"int":".int.kml","cor":".cor.kml","amp1":".amp1.kml","amp2":".amp2.kml","unw":".unw.kml","hgt":".hgt.kml"}
    for filetype in filelist.keys():
        filename = dataname + filelist[filetype]
        if os.path.exists(filename):
            continue
        aurl = os.path.join(baseurl,filename)
        os.system("wget " + aurl)


def main():
    """test kml function"""
    uid = "1540"
    dataname = "SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01"
    overview_kml(uid, dataname)

if __name__ == "__main__":
    main()