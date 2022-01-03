# UAVSAR Processing

## Processing procedures
Before the processing, run **init.py** first, check .netrc
```
processing_main.py -j job.csv
    
    -- download and covert unw.grd and hgt.grd to geotiff
    -- download overview kml (downloadkml.py)
    -- generate thumbnail.tiff (downloadkml.py)
    -- update metadata (metadata.py)
    -- generate alternative coloring (sldtool.py) 
```

sample job csv:
```
1540,SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01
1541,SanAnd_08503_12130-002_13095-013_0196d_s01_L090HH_01
```
folder structure is defined in uavsar_processing.cfg  
```
GeoGateway/
├── processing
│   ├── ann
│   ├── color
│   ├── highres
│   ├── kml
│   │   ├── uid1540
│   │   └── uid1541
│   ├── logs
│   └── thumbnail
└── products
    ├── uid_1540
    └── uid_1541
```
metadata is saved in geojson format: 
```
1540-1541.geojson 
{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
"features": [
{ "type": "Feature", "properties": { "dataname": "SanAnd_08503_12023-008_13095-013_0387d_s01_L090HH_01", "description": "San Andreas Fault - Salton Trough, CA", "lines": 5384, "samples": 10030, "startlat": 32.91524412, "startlon": -117.2652138, "latspace": -5.556e-05, "lonspace": 5.556e-05, "wavelength": 23.8403545, "gpslatitude": 12495.5197, "terrainheight": 231.635643, "peglat": 32.6212824, "peglon": -116.960323, "peghead": 85.1807499, "radardirection": "Left", "time1": "2-May-2012 01:37:25 UTC", "time2": "24-May-2013 02:24:59 UTC", "phasesign": -1.0, "version": 2.0, "url": "http://uavsar.jpl.nasa.gov/cgi-bin/product.pl?jobName=SanAnd_08503_12023-008_13095-013_0387d_s01_L090_01", "unw": 1, "UID": "1540" }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -117.26581082, 32.8456677 ], [ -116.72907621, 32.88647427 ], [ -116.7091961, 32.69769629 ], [ -117.24370659, 32.64494379 ], [ -117.26581082, 32.8456677 ] ] ] } },
{ "type": "Feature", "properties": { "dataname": "SanAnd_08503_12130-002_13095-013_0196d_s01_L090HH_01", "description": "San Andreas Fault - Salton Trough, CA", "lines": 5382, "samples": 10031, "startlat": 32.91668868, "startlon": -117.24432324000001, "latspace": -5.556e-05, "lonspace": 5.556e-05, "wavelength": 23.8403545, "gpslatitude": 12495.2844, "terrainheight": 244.030913, "peglat": 32.6213699, "peglon": -116.959095, "peghead": 85.180788, "radardirection": "Left", "time1": "9-Nov-2012 02:35:53 UTC", "time2": "24-May-2013 02:25:07 UTC", "phasesign": -1.0, "version": 2.0, "url": "http://uavsar.jpl.nasa.gov/cgi-bin/product.pl?jobName=SanAnd_08503_12130-002_13095-013_0196d_s01_L090_01", "unw": 1, "UID": "1541" }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -117.24353884, 32.8468661 ], [ -116.70648665, 32.88786628 ], [ -116.68925615, 32.69621279 ], [ -117.22519926, 32.64628607 ], [ -117.24353884, 32.8468661 ] ] ] } }
]
}

```