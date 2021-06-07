# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache    
from tqdm import trange
import pandas as pd

from pynsee.localdata._get_insee_local_onegeo import _get_insee_local_onegeo

@lru_cache(maxsize=None)
def _warning_future_dev():
    print("\n!!! This function is still at an early development stage,\nfuture changes are likely !!!")

def get_local_data(variables, dataset_version, nivgeo='FE', geocodes=['1']):
    """Get INSEE local numeric data

    Args:
        variables (str): one or several variables separated by an hyphen (see get_local_metadata)

        dataset_version (str): code of a dataset version (see get_local_metadata)

        nivgeo (str): code of kind of French administrative area (see get_nivgeo_list), by default it is 'FE' ie all France
        
        geocodes (list): code one specific area (see get_geo_list), by default it is ['1'] ie all France

    Raises:
        ValueError: Error if geocodes is not a list
    
    Examples:
        >>> from pynsee.localdata import *
        >>> metadata = get_local_metadata()
        >>> nivgeo = get_nivgeo_list()
        >>> departement = get_geo_list('departements')
        >>> #
        >>> data_all_france = get_local_data(dataset_version='GEO2020RP2017',
        >>>                        variables =  'SEXE-DIPL_19')
        >>> #
        >>> data_91_92 = get_local_data(dataset_version='GEO2020RP2017',
        >>>                        variables =  'SEXE-DIPL_19',
        >>>                        nivgeo = 'DEP',
        >>>                        geocodes = ['91','92'])
    """    
        
    if type(geocodes) != list:
        raise ValueError("!!! geocodes must be a list !!!")    
    
    list_data_all = []
    
    for cdg in trange(len(geocodes), desc = "Getting data"): 
        
        codegeo = geocodes[cdg]
        
        df = _get_insee_local_onegeo(variables, dataset_version, nivgeo, codegeo)
        
        list_data_all.append(df)
 
    data_final = pd.concat(list_data_all).reset_index(drop=True)
        
    _warning_future_dev()
    
    return(data_final)
           