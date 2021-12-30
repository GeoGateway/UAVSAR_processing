"""
utilities.py
routines shared across the modules
"""

import os

def create_path(apath):
    """check a path, if not existing, then create one"""
    if not os.path.exists(apath):
        os.makedirs(apath, exist_ok=True)
