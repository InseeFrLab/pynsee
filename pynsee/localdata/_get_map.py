# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import numpy as np

from pynsee.localdata.get_map_link import get_map_link

@lru_cache(maxsize=None)
def _get_map(geo):
    """Get geopandas dataframe from French administrative area

    Args:
        geo (str): French administrative area (see get_map_list)
    
    Notes:
        All data come from https://france-geojson.gregoiredavid.fr/, made from INSEE and IGN data in 2018.

        Only arrondissements municipaux data come from https://public.opendatasoft.com/explore/dataset/arrondissements-millesimes0/information/ in 2020.

    Examples:
        >>> from pynsee.localdata import *
        >>> from pynsee.localdata._get_map import _get_map
        >>> map_list = get_map_list()
        >>> map_departement = _get_map('departements')
        >>> # Draw map with random values
        >>> import matplotlib, descartes
        >>> map_departement.plot(column='value')
    """            
    import geopandas as gpd
    map = gpd.read_file(get_map_link(geo))

    map['value'] = np.random.randint(1, 10, map.shape[0])
   
    return(map)

