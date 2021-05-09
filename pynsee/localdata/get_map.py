# -*- coding: utf-8 -*-
from functools import lru_cache
import numpy as np

from pynsee.localdata.get_map_link import get_map_link

@lru_cache(maxsize=None)
def _warning_map(geo):
    if geo == 'arr' :
        msg1 = '!!! Geographic data made on arrondissements municipaux in 2020 come from opendatasoft\n'
        msg2 = 'https://public.opendatasoft.com/explore/dataset/arrondissements-millesimes0/information/ !!!'
    else:
        msg1 = '!!! Geographic data come from https://france-geojson.gregoiredavid.fr/,\n'
        msg2 = 'It has been made in 2018 from INSEE and IGN data !!!'
   
    print('{}{}'.format(msg1, msg2))

@lru_cache(maxsize=None)
def get_map(geo):
    """Get geopandas dataframe from French administrative area

    Args:
        geo (str): French administrative area (see get_map_list)
    
    Notes:
        All data come from https://france-geojson.gregoiredavid.fr/, made from INSEE and IGN data in 2018.

        Only arrondissements municipaux data have been downloaded come from https://public.opendatasoft.com/explore/dataset/arrondissements-millesimes0/information/ in 2020.

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
        _warning_map('arr')
        map = map[['code_insee', 'nom_com','geometry']]
        map.columns = ['code', 'nom', 'geometry']
    else:
        _warning_map('other')

    map['value'] = np.random.randint(1, 10, map.shape[0])
   
    return(map)

