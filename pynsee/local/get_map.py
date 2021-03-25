# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def get_map(geo):

    # test
    # import matplotlib
    # import descartes
    # map = get_map('communes')
    # map.plot(column='value')
    
    import geopandas as gpd
    import numpy as np
    
    from pynsee.local.get_map_link import get_map_link
    
    map = gpd.read_file(get_map_link(geo))

    map['value'] = np.random.randint(1, 10, map.shape[0])
   
    return(map)