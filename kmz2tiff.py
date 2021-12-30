"""
kmz2tiff.py
   -- merge high resoulition images in kmls to one geotiff
"""

# Version: ImageMagick 6.9.10-23 Ubuntu 20.04

import sys,os,string,glob,math
import shutil
import xml.etree.ElementTree as ET
from PIL import Image

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
    f.closed
    
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
    
def getint(name):
    """ sort kml by int """
    
    basename = string.split(name,os.path.sep)[-1][:-4]
    alpha, num = basename.split("-")
    return int(num)

def parse_kml(dockml):
    """ parse doc.kml """

    bboxlist=[]
    tree = ET.parse(dockml)
    for groundoverlay in tree.iter(tag="{http://www.opengis.net/kml/2.2}GroundOverlay"):
        V = {}
        for elem in groundoverlay:
            if "name" in elem.tag:
                V['name'] = elem.text
                continue
            if "LatLonBox" in elem.tag:
                for latlon_elem in elem:
                    pos_tag = latlon_elem.tag.replace('{http://www.opengis.net/kml/2.2}','')
                    V[pos_tag]=float(latlon_elem.text)
        if "tile" in V['name']:
            bboxlist.append(V)
    return bboxlist

def processing_kml(kmlfolder, outputfolder):
    """ processing kml folder """
    
    # older version
    newversion = True
    geotiff = os.path.basename(kmlfolder)+".tiff"
    geotiff_compressed = os.path.basename(kmlfolder)+"_compressed.tiff"


    kmls = glob.glob(kmlfolder + os.path.sep + "tile-*.kml")
    if not len(kmls) == 0:
        newversion = False
        # sort by number from 0 ~ xxx
        kmls.sort(key=getint)
    
        #cmd = "gdal_merge.py -o /tmp/uid10_int.tif"
        cmd = "montage"
        # need to find out west most tile
        # need to find out east most tile
        bboxlist = []
        totalwidth, totalheight = 0, 0
        for kml in kmls:
            #print kml
            tile = string.split(kml, os.path.sep)[-1][:-4]
            bbox = extractbbox(kml)
            bboxlist.append(bbox)
            image = kmlfolder + os.path.sep + "images" + os.path.sep + tile + ".png"
            imagesize = getimagesize(image)
            totalwidth += imagesize[0]
            totalheight += imagesize[1]
            #generateworldfile(image, bbox, imagesize)     
            cmd += " " + tile + ".png"
    #os.chdir(kmlfolder + os.path.sep + "images")
    # new version
    if newversion:
        totalwidth, totalheight = 0, 0
        cmd = "montage"
        dockml = kmlfolder + os.path.sep + "doc.kml"
        bbox_dict = parse_kml(dockml)
        #[west,east,north,south]
        for item in bbox_dict:
            image = kmlfolder + os.path.sep + "images" + os.path.sep + item['name']
            imagesize = getimagesize(image)
            totalwidth += imagesize[0]
            totalheight += imagesize[1]
            #generateworldfile(image, bbox, imagesize)     
            cmd += " " + item['name']
        bboxlist = []
        bboxlist.append([bbox_dict[0]['west'],bbox_dict[0]['east'],bbox_dict[0]['north'],bbox_dict[0]['south']])
        bboxlist.append([bbox_dict[-1]['west'],bbox_dict[-1]['east'],bbox_dict[-1]['north'],bbox_dict[-1]['south']])
 

    uppercorner = bboxlist[0]
    lowercorner = bboxlist[-1]
    lonspan = lowercorner[1]-uppercorner[0]
    latspan = lowercorner[3]-uppercorner[2]
    #[west,east,north,south]
    bbox = [uppercorner[0],lowercorner[1],uppercorner[2],lowercorner[3]]
    row = int(math.ceil(lonspan / (uppercorner[1]-uppercorner[0])))
    col = int(math.ceil(latspan / (uppercorner[3]-uppercorner[2])))
    print(row,col)
    realwidth, realheight = totalwidth/col, totalheight/row
    totalimage = kmlfolder + os.path.sep + "images" + os.path.sep + "alltest.png"
    generateworldfile(totalimage, bbox, [realwidth,realheight]) 
    
    #gdalfunction -srcnodata 0
    #gdal_translate -a_nodata 0 -b 1 -b 2 -b 3 -mask 4 alltest.png alltest.tiff -a_srs EPSG:4326
    #gdal_translate -a_nodata 0 alltest.tiff -co COMPRESS=DEFLATE -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 alltest_compress.tiff
    #gdaladdo -r average alltest_compress.tiff 2 4 8 16 32
    # change folder to images folder
    os.chdir(kmlfolder + os.path.sep + "images")
    cmd += " -tile "+str(row)+"x" + str(col) +" -geometry +0+0 -depth 8 -background none PNG32:alltest.png"
    print("mosaic image ...")
    os.system(cmd)
    
    print("gdal_translate image ...")
    #gdal_translate -a_nodata 0 -b 1 -b 2 -b 3 -mask 4 alltest.png alltest.tiff -a_srs EPSG:4326
    cmd = "gdal_translate alltest.png "+ geotiff + " -a_srs EPSG:4326"
    os.system(cmd)
    #gdal_translate -a_nodata 0 alltest.tiff -co COMPRESS=DEFLATE -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 alltest_compress.tiff
    cmd = "gdal_translate " + geotiff + " -co COMPRESS=DEFLATE -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 "+ geotiff_compressed
    os.system(cmd)
    #gdaladdo -r average alltest_compress.tiff 2 4 8 16 32
    cmd = "gdaladdo -r average "+ geotiff_compressed + " 2 4 8 16 32 64"
    os.system(cmd)
    print ("done !")

    # move all tiff file
    #cmd = "mv *.tiff " + outputfolder
    #print "moved tiffs"
    # only move compressed tiff
    cmd = "mv " + geotiff_compressed + " " + outputfolder
    print("moved compressed tiff")
    os.system(cmd)

    return

def convert_kmz(kmz,outputfolder):
    """ convert kmz to tiff """

    # first unzip kmz file
    # uzip kmz -d dir
    kmzfolder = kmz[:-4] 
    cmd = "unzip " + kmz + " -d " + kmzfolder
    #print cmd
    os.system(cmd)
    processing_kml(kmzfolder,outputfolder)

    # chdir then delete folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # remove kmz folder
    try:
        shutil.rmtree(kmzfolder)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

    return

def main():

    kmzs = ["uid1540@SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01.unw.kmz",
        "uid1541@SanAnd_08503_12130-002_13095-013_0196d_s01_L090HH_01.unw.kmz"]
    outputfolder = "/home/cicuser/Downloads/coding"
    for kmz in kmzs:
        convert_kmz(kmz,outputfolder)


if __name__ == "__main__":
    main()
