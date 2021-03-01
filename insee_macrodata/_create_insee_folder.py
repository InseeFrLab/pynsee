# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 22:52:53 2021

@author: XLAPDO
"""

def _create_insee_folder():
    import os 
    import tempfile
    import appdirs
        
    try:
        from ._hash import _hash
        #find local folder
        local_appdata_folder = appdirs.user_cache_dir()      
        insee_folder = local_appdata_folder + '/insee'
        
        #create insee folder
        if not os.path.exists(insee_folder):
            os.mkdir(insee_folder)
            
        insee_folder = insee_folder + '/py_insee'
        
        #create insee folder
        if not os.path.exists(insee_folder):
            os.mkdir(insee_folder)
        
        #test if saving a file is possible
        test_file = insee_folder + '/' + _hash('test_file')
        with open(test_file, 'w') as f:
            f.write('')
        
    except:
        #if error temporary folder is returned
        insee_folder = tempfile.mkdtemp()
    finally:
        return(insee_folder)