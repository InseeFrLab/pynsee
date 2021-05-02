# -*- coding: utf-8 -*-
from functools import lru_cache
import numpy as np

from pynsee.localdata.get_map_link import get_map_link

@lru_cache(maxsize=None)
def _warning_arr_muni():
    msg1 = '!!! Geographic data on arrondissements municipaux come from another source,\n'
    msg2 = 'therefore small gaps may be visible !!!'
    print('{}{}'.format(msg1, msg2))

@lru_cache(maxsize=None)
def get_map(geo):
    """Get geopandas dataframe from French administrative area

    Args:
        geo (str): French administrative area (see get_map_list)

    Examples:
        >>> from pynsee.localdata import *
        >>> map_list = get_map_list()
        >>> map_departement = get_map('departements')
        >>> # Draw map with random values
        >>> import matplotlib, descartes
        >>> map_departement.plot(column='value')
    """            
    import geopandas as gpd
    map = gpd.read_file(get_map_link(geo))

    if geo == 'arrondissements-municipaux':
        _warning_arr_muni()
        map = map[['code_insee', 'nom_com','geometry']]
        map.columns = ['code', 'nom', 'geometry']

    map['value'] = np.random.randint(1, 10, map.shape[0])
   
    return(map)

