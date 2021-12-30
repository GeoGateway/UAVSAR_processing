"""
downloadkml.py
    -- download overview kml
    -- fix kml
    -- generate thumbnail with int.png
"""
import os
import settings
from PIL import Image

from utilities import create_path

def cleanStrings(inStr, leftstr,rightstr):
    a = inStr.find(leftstr)
    b = inStr.find(rightstr)

    if a < 0 and b < 0:
        return False

    return inStr[a + len(leftstr):b]

def getimagesize(image_file):
    """ return image size """
    
    img = Image.open(image_file)
    width,height = img.size
    
    return [width, height]

def extractbbox(kml):
    """ find boundingbox from a kml """
    
    with open(kml,"r") as f:
        kmlstring = f.read()
    
    #<north>32.93182878</north>
    #<south>32.87493534</south>
    #<east>-116.0291427</east>
    #<west>-116.08603614</west>
    
    north = cleanStrings(kmlstring, "<north>","</north>")
    south = cleanStrings(kmlstring, "<south>","</south>")
    east  = cleanStrings(kmlstring, "<east>","</east>")
    west  = cleanStrings(kmlstring, "<west>","</west>")
    
    bbox = map(float,[west,east,north,south])

    return bbox

def generateworldfile(image_file,bbox,imagesize):
    """ write the world file """
    
    # reference: http://en.wikipedia.org/wiki/World_file
    # Line 1: A: pixel size in the x-direction in map units/pixel
    # Line 2: D: rotation about y-axis
    # Line 3: B: rotation about x-axis
    # Line 4: E: pixel size in the y-direction in map units, almost always negative[3]
    # Line 5: C: x-coordinate of the center of the upper left pixel
    # Line 6: F: y-coordinate of the center of the upper left pixel
    
    # no rotation in our case
    world_file = image_file[:-4] + ".pgw"
    
    [west,east,north,south] = bbox
    [width, height] = imagesize
    with open(world_file,'w') as f:
        
        xsize = (east - west) / width
        ysize = (south - north) / height
        xul = west
        yul = north
        
        f.write("%.8f" % xsize + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("%.8f" % ysize + "\n")
        f.write("%.8f" % xul + "\n")
        f.write("%.8f" % yul + "\n")
        
    return

def generate_thumbnail(uid, dataname, itype):
    """generate thumbnail"""

    kml = "{}.{}.kml".format(dataname,itype)
    png = "{}.{}.png".format(dataname,itype)

    # generate pgw
    bbox = extractbbox(kml)
    imagesize = getimagesize(png)
    generateworldfile(png, bbox, imagesize)

    # convert to tiff
    tiff = "uid" + uid + "_int.tiff"
    # force it to be 8bit tiff
    cmd = "gdal_translate -a_srs EPSG:4326 " + png + " " + tiff
    os.system(cmd)

    tiffc = "uid" + uid + "_int_t.tiff"
    cmd = "gdal_translate -of GTiff -ot Byte -scale -a_srs EPSG:4326 " + tiff + " -outsize 50% 50% -co TILED=YES " + tiffc
    os.system(cmd)
    cmd = "gdaladdo -r average " + tiffc + " 2 4 8"
    os.system(cmd)
    
    # remove and move
    os.system("rm " + tiff)
    os.system(cmd)

    cmd = "mv " + tiffc + " " + settings.THUMBNAIL_DIR 
    os.system(cmd)

    return

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
        else:
            kstrnew = kstr

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
        
        #write out the new kml
        with open(kmlfile,"w") as f:
            f.write(kstrnew)

    generate_thumbnail(uid, dataname,"int")

def main():
    """test kml function"""
    uid = "1540"
    dataname = "SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01"
    overview_kml(uid, dataname)

if __name__ == "__main__":
    main()