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
metadata is saved in geojson format: [1540_1541.geojson](sample/ann/1540_1541.geojson)

```
