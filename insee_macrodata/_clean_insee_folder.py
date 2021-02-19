# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 14:51:04 2021

@author: XLAPDO
"""

def _clean_insee_folder():
    import appdirs
    import os
    
    local_appdata_folder = appdirs.user_cache_dir()      
    insee_folder = local_appdata_folder + '/insee' + '/py_insee'
    
    # delete all files in the folder
    if not os.path.exists(insee_folder):
        list_file_insee = os.listdir(insee_folder)
        if len(list_file_insee) > 0:
            for f in list_file_insee:
                os.remove(insee_folder + '/' + f)    