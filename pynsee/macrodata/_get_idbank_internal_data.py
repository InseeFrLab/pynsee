# -*- coding: utf-8 -*-

import zipfile
import pkg_resources
import pandas as pd
import os

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
    
#from functools import lru_cache

#@lru_cache(maxsize=None)
def _get_idbank_internal_data():
    
    insee_folder = _create_insee_folder()
    
    data_file = insee_folder + '/' + 'idbank_list_internal.csv'
    data_final_file = insee_folder + '/' + _hash('idbank_list_internal_final')
    zip_file = pkg_resources.resource_stream(__name__, 'data/idbank_list_internal.zip')
    
    if not os.path.exists(data_final_file):
       
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)            
            
        idbank_list = pd.read_csv(data_file, encoding = 'latin-1',
                                  quotechar='"', sep=',', dtype=str, usecols = [0,1,2,538,539])
        
        os.remove(data_file)
        idbank_list.to_pickle(data_final_file)
    else:  
        # pickle format depends on python version
        # then read_pickle can fail, if so
        # the file is removed and the function is launched again
        # testing requires multiple python versions      
        try:            
            idbank_list = pd.read_pickle(data_final_file)
        except:
            os.remove(data_final_file)
            idbank_list = _get_idbank_internal_data()
        #else:
        #   print('Cached data used')
    
    return idbank_list