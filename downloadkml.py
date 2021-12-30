"""
downloadkml.py
    -- download overview kml
    -- fix kml
"""
import os
import settings

from utilities import create_path

def cleanStrings(inStr, leftstr,rightstr):
    a = inStr.find(leftstr)
    b = inStr.find(rightstr)

    if a < 0 and b < 0:
        return False

    return inStr[a + len(leftstr):b]

def overview_kml(uid, dataname):
    """download kml"""

    # kml/uid1540
    kmlfolder = os.path.join(settings.KML_DIR, "uid"+uid)
    create_path(kmlfolder)
    os.chdir(kmlfolder)
       
    baseurl = "http://uavsar.jpl.nasa.gov/kml/RPI/"
    
    # download kml
    filelist = {"int":".int.kml","cor":".cor.kml","amp1":".amp1.kml","amp2":".amp2.kml","unw":".unw.kml","hgt":".hgt.kml"}
    for filetype in filelist.keys():
        filename = dataname + filelist[filetype]
        if os.path.exists(filename):
            continue
        aurl = os.path.join(baseurl,filename)
        os.system("wget " + aurl)

    # download image in kml
    for filetype in filelist.keys():
        kmlfile = dataname + filelist[filetype]
        with open(kmlfile,"r") as f:
            kstr = f.read()   
        pngurl = cleanStrings(kstr, "<href>","</href>")
        wget = "wget " + pngurl
        os.system(wget)

        # get image name
        png = os.path.basename(pngurl)
        # some png has hash
        #http://downloaduav.jpl.nasa.gov/kml/RPI/SanAnd_26516_16048-011_16059-004_0082d_s01_L090HH_01.amp1.png?hash=f81945f9599d17e24aff7c0bebd2243c
        if "?hash" in png:
            nohashpng = png.split("?hash")[0]
            cmd = "cp " + png + " " + nohashpng
            os.system(cmd)
        
        # move old kml as kml.org
        mv = "mv " + kmlfile + " " + kmlfile+".org"
        os.system(mv)
   
        # get rid of placemark
        placemark = cleanStrings(kstr, "<Placemark>","</Placemark>")
        #print placemark
        if placemark: 
            kstrnew = kstr.replace("<Placemark>"+placemark+"</Placemark>","")

        # replace image url
        kstrnew = kstrnew.replace(pngurl, png)

        # handle screenoverlay
        if "<ScreenOverlay>" in kstrnew:
            screenoverlay = cleanStrings(kstrnew, "<ScreenOverlay>","</ScreenOverlay>")
            legendurl = cleanStrings(screenoverlay, "<href>","</href>")
            cmd = "wget " + legendurl
            os.system(cmd)
            legendpng = os.path.basename(legendurl)
            screenoverlay_new = screenoverlay.replace(legendurl,legendpng)
            kstrnew = kstrnew.replace("<ScreenOverlay>"+screenoverlay+"</ScreenOverlay>","<ScreenOverlay>"+screenoverlay_new+"</ScreenOverlay>")
        
        with open(kmlfile,"w") as f:
            f.write(kstrnew)


def main():
    """test kml function"""
    uid = "1540"
    dataname = "SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01"
    overview_kml(uid, dataname)

if __name__ == "__main__":
    main()