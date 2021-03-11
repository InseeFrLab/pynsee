# -*- coding: utf-8 -*-

def get_map(geo):
    
    #import geopandas as gpd
    import os
    import zipfile
    import pkg_resources
    
    from pynsee.local import _get_maps_list
    #from ._get_internal_maps import _get_internal_maps
    #from ._get_maps_list import _get_maps_list
    from pynsee.utils import _create_insee_folder
    
    insee_folder = _create_insee_folder()

    insee_folder_map = insee_folder + '/' + 'maps'
    if not os.path.exists(insee_folder_map):
        os.mkdir(insee_folder_map)        
        
    maps_list = _get_maps_list()
    
    if geo in maps_list['name_fr']:     
        
        geo_file = insee_folder_map + '/' + geo + '.geojson'
        if os.path.exists(geo_file):
            #map = gpd.read_file(geo_file)
            return(geo_file)
        else:
            # unzip files stored in package
            zip_file = pkg_resources.resource_stream(__name__, 'data/maps.zip')
    
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(insee_folder)    
            
            if os.path.exists(geo_file):
                #map = gpd.read_file(geo_file)
                return(geo_file)
            else:
                raise ValueError('Package error : %s is missing' % geo_file)
    else:
        raise ValueError('%s is not in the list coming from get_maps_list' % geo)