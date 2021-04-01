# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_future_dev():
    print("!!! This function is still at an early development stage,\nfuture changes are likely !!!")

def get_insee_local(variables, dataset_version, nivgeo, geocodes):
    """Get INSEE local numeric data

    Args:
        variables (str): one or several variables separated by an hyphen (see get_local_metadata)
        dataset_version (str): code of a dataset version (see get_local_metadata)
        nivgeo (str): code of kind of French administrative area (see get_nivgeo_list)
        geocodes (list): code one specific area (see get_geo_list)

    Raises:
        ValueError: Error if geocodes is not a list
    
    Examples:
        >>> from pynsee.local import *
        >>> metadata = get_local_metadata()
        >>> nivgeo = get_nivgeo_list()
        >>> departement = get_geo_list('departements')
        >>> data = get_insee_local(dataset_version='GEO2020RP2017',
        >>>                        variables =  'SEXE-DIPL_19',
        >>>                        nivgeo = 'DEP',
        >>>                        geocodes = ['91','92'])
    """    
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
           