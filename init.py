"""
init.py
    -- create folders for processing
    -- check netrc for the downloading
"""

import os, sys
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.join(BASE_DIR,"uavsar_processing.cfg"))

items = config.items("general")
for key, apath in items:
    apathfull = os.path.expanduser(apath)
    if not os.path.exists(apathfull):
        print(f"creating: {key} {apath}")
        os.makedirs(apathfull, exist_ok=True)

# https://urs.earthdata.nasa.gov/documentation/for_users/data_access/curl_and_wget
homedir = os.path.expanduser("~")
print(homedir)
os.chdir(homedir)
if not os.path.exists(".netrc"):
    print("create .netrc")
    cmd = "touch .netrc"
    os.system(cmd)
    cmd = 'echo "machine urs.earthdata.nasa.gov login quakesimuser password ???" > .netrc'
    os.system(cmd)
    cmd = "chmod 0600 .netrc"
    os.system(cmd)
    print("please fill in the password in .netrc")

if not os.path.exists(".urs_cookies"):
    print("create .usr_cookies")
    cmd = "touch .urs_cookies"
    os.system(cmd)
