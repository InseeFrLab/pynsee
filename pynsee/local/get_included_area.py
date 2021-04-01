# -*- coding: utf-8 -*-
#from functools import lru_cache
#
#@lru_cache(maxsize=None)
def get_included_area(area_type, codeareas):
    """Get all areas included in the list of areas provided

    Args:
        area_type (str): type of area
        codeareas (str): list of areas

    Raises:
        ValueError: Error if codeareas is not a list

    Examples:
        >>> from pynsee.local import *
        >>> paris_empl_area = get_included_area(area_type = 'zonesDEmploi2020', codeareas = ['1109'])
    """    
#    codeareas = ['1109']
#    area_type = 'zonesDEmploi2020'
    from pynsee.local._get_insee_one_area import _get_insee_one_area
    
    import pandas as pd    
    from tqdm import trange
    
    if type(codeareas) != list:
        raise ValueError("!!! codeareas must be a list !!!")
    
    list_data = []    
    
    for c in trange(len(codeareas)):   
        list_data.append(_get_insee_one_area(area_type, codeareas[c]))

    data_final = pd.concat(list_data)
    data_final = data_final.assign(area_type=area_type)
    
    return(data_final)
    