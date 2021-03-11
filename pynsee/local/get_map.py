# -*- coding: utf-8 -*-



def get_map(geo):
    
    import geopandas as gpd
    import os
    
    from pynsee.local import _get_internal_maps
    from pynsee.local import _get_maps_list
    from pynsee.utils import _create_insee_folder
    
    insee_folder_map = _create_insee_folder(folder='maps')
    
    # unzip files stored in package
    _get_internal_maps()
    
    maps_list = _get_maps_list()
    
    if geo in maps_list['name_fr']:
        geo_file = insee_folder_map + '/' + geo + '.geojson'
        if os.path.exists(geo_file):
            sf = gpd.read_file(geo_file)


import numpy as np
sf['value'] = np.random.randint(1, 10, sf.shape[0])

import matplotlib
import descartes
sf.plot(column='value')
        
        
