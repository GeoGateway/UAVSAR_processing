"""
settings.py
    -- load configration
"""

import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.join(BASE_DIR,"uavsar_processing.cfg"))

WORKING_DIR = os.path.expanduser(config.get('general','WORKING_DIR'))
PRODUCT_DIR = os.path.expanduser(config.get('general','PRODUCT_DIR'))
KML_DIR = os.path.expanduser(config.get('general','KML_DIR')) 
THUMBNAIL_DIR = os.path.expanduser(config.get('general','THUMBNAIL_DIR'))
LOG_DIR = os.path.expanduser(config.get('general','LOG_DIR')) 

# creat folders if necessary
for apath in [WORKING_DIR,PRODUCT_DIR,KML_DIR,THUMBNAIL_DIR, LOG_DIR]:
    if not os.path.exists(apath):
        os.makedirs(apath, exist_ok=True)
