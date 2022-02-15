# -*- coding: utf-8 -*-

import os
import re
import pandas as pd
from tqdm import trange

from pynsee.geodata._get_full_list_wfs import _get_full_list_wfs

from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def get_geodata_list(update=False):
    """Get a list of geographical limits of French administrative areas from IGN API

    Args:
        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False.
    
    Examples:
        >>> from pynsee.geodata import get_geodata_list
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
    """    
    
    format = "WFS"
    topic = "administratif"
    version = "2.0.0"
        
    pynsee_folder = _create_insee_folder()
    file_name = pynsee_folder + '/' +  _hash("".join(topic + format)) + ".csv"  
    
    if (not os.path.exists(file_name)) | (update is True):
                
        data_full_list = _get_full_list_wfs(topic=topic, version=version)
                    
        if len(data_full_list)>0:
            list_var = ['Name', 'Identifier', 'Title', 'DefaultCRS', 'SupportedCRS',
                            'TileMatrixSet', 'Abstract', 'LegendURL', 'Format']

            list_col = [col for col in data_full_list.columns if col in list_var]
                
            data_list = data_full_list[list_col]
            data_list = data_list.drop_duplicates().reset_index(drop=True)
                                
            if 'Name' in data_list.columns:
                data_list.rename(columns={'Name':'Identifier'}, inplace=True)
                
            data_list['DataFormat'] = format
            data_list['Topic'] = topic
            data_list['ApiVersion'] = version                  
            
        data_all = data_list.reset_index(drop=True)

        print('\nData saved : {}'.format(file_name))
        
        data_all.to_pickle(file_name)
    else:        
        try:
            data_all = pd.read_pickle(file_name)
        except:
            os.remove(file_name)
            data_all = get_geodata_list(update=True)
        else:
            _warning_cached_data(file_name)
    
    # set column order
    first_col = ['Topic', 'DataFormat', 'ApiVersion', 'Identifier', 'Abstract', 'Title', 'ZoomRange']
    available_col = [col for col in first_col if col in data_all.columns]
    other_col = [col for col in data_all.columns if col not in available_col]
    
    data_all = data_all[available_col + other_col]
    
    return(data_all)
    
