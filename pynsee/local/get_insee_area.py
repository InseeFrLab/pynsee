# -*- coding: utf-8 -*-
#from functools import lru_cache
#
#@lru_cache(maxsize=None)
def get_insee_area(area_type, codeareas):
    
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
    