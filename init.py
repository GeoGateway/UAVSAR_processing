"""
init.py
    -- create folders for processing
"""

import os, sys
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.join(BASE_DIR,"uavsar_processing.cfg"))

items = config.items("general")
for key, apath in items:
    if not os.path.exists(apath):
        print(f"creating: {key}")
        os.makedirs(os.path.expanduser(apath), exist_ok=True)
