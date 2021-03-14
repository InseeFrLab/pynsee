# -*- coding: utf-8 -*-

def _get_local_metadata():
    
    #import geopandas as gpd
    import os
    import zipfile
    import pkg_resources
    
    from pynsee.utils._create_insee_folder import _create_insee_folder
    
    insee_folder = _create_insee_folder()

    insee_folder_local_metadata = insee_folder + '/' + 'local_metadata'
    if not os.path.exists(insee_folder_local_metadata):
        os.mkdir(insee_folder_local_metadata)        
    
    zip_file = pkg_resources.resource_stream(__name__, 'data/local_metadata.zip')
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(insee_folder) 