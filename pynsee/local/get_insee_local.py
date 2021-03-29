# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_future_dev():
    print("!!! This function is still at an early development stage,\nfuture changes are likely !!!")

def get_insee_local(variables, dataset_version, nivgeo, geocodes):
    
    from pynsee.local._get_insee_local_onegeo import _get_insee_local_onegeo
    
    from tqdm import trange
    import pandas as pd
    
    if type(geocodes) != list:
        raise ValueError("!!! geocodes must be a list !!!")
        
    _warning_future_dev()
    
#    variables = 'AGESCOL-SEXE-ETUD';dataset_version = 'GEO2019RP2011';geocodes = ['91','92', '976'];nivgeo = 'DEP'
      
    list_data_all = []
    
    for cdg in trange(len(geocodes), desc = "Getting data"): 
        
        codegeo = geocodes[cdg]
        
        df = _get_insee_local_onegeo(variables, dataset_version, nivgeo, codegeo)
        
        list_data_all.append(df)
 
    data_final = pd.concat(list_data_all).reset_index(drop=True)
        
    return(data_final)
           