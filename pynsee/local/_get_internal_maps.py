# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 08:47:32 2021

@author: eurhope
"""

import zipfile
import pkg_resources
#import pandas as pd
#import os
    
#from functools import lru_cache

#@lru_cache(maxsize=None)
def _get_internal_maps():
    
    from pynsee.utils import _create_insee_folder
#    from pynsee.utils import _hash
    
    insee_folder_maps = _create_insee_folder(folder='maps')
    
    zip_file = pkg_resources.resource_stream(__name__, 'data/maps.zip')
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(insee_folder_maps)         
            
    
