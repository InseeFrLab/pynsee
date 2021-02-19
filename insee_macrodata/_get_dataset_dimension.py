# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 17:56:28 2020

@author: eurhope
"""
# from functools import lru_cache

# @lru_cache(maxsize=None)
def _get_dataset_dimension(dataset) :
    
    import requests     
    import tempfile
    import xml.etree.ElementTree as ET
    import pandas as pd
    import os
    from datetime import datetime 
    
    from ._create_insee_folder import _create_insee_folder
    from ._hash import _hash
    
    INSEE_sdmx_link_datastructure = "https://www.bdm.insee.fr/series/sdmx/datastructure/FR1"
        
    INSEE_sdmx_link_datastructure_dataset = INSEE_sdmx_link_datastructure + '/' + dataset
    
    insee_folder = _create_insee_folder()
    file = insee_folder + "/" + _hash(INSEE_sdmx_link_datastructure_dataset)
        
    trigger_update = False
        
    # if the data is not saved locally, or if it is too old (>90 days)
    # then an update is triggered
    
    if not os.path.exists(file): 
        trigger_update = True
    else:       
        # from datetime import timedelta 
        # insee_date_time_now = datetime.now() + timedelta(days=91)
        insee_date_time_now = datetime.now()
         
        # file date creation
        file_date_last_modif =  datetime.fromtimestamp(os.path.getmtime(file))
        day_lapse = (insee_date_time_now - file_date_last_modif).days
        
        if day_lapse > 90:
            trigger_update = True   

    if trigger_update :
        proxies = {'http': os.environ.get('http'),
               'https': os.environ.get('https')}
    
        #download file    
        results = requests.get(INSEE_sdmx_link_datastructure_dataset, proxies = proxies)
        
        # create temporary directory
        dirpath = tempfile.mkdtemp()
        
        dataset_dimension_file = dirpath + '\\dataset_dimension_file'
        
        with open(dataset_dimension_file, 'wb') as f:
            f.write(results.content)
        
        root = ET.parse(dataset_dimension_file).getroot()
        
        data = root[1][0][0][2][0]
    
        n_dimension  = len(data)
        
        list_dimension = []
        
        def extract_local_rep(data, i):
            try:
                local_rep = next(iter(data[i][1][0][0].attrib.values()))            
            except:
                local_rep = None
            finally:
                return(local_rep);
            
        def extract_id(data, i):
            try:
                id_val = next(iter(data[i].attrib.values()))         
            except:
                id_val = None
            finally:
                return(id_val);
        
        for i in range(0, n_dimension):
            
            dimension_id = extract_id(data, i)
            local_rep = extract_local_rep(data, i)
            
            dimension_df = {
                'dataset': [dataset],
                'dimension': [dimension_id],
                'local_representation': [local_rep]}
        
            dimension_df = pd.DataFrame(dimension_df,
                              columns = ['dataset', 'dimension', 'local_representation'])
            
            list_dimension.append(dimension_df)
        
        dimension_df_all = pd.concat(list_dimension)      
        dimension_df_all = dimension_df_all.dropna() 
        
        # save data
        dimension_df_all.to_pickle(file)
    
    else:          
        dimension_df_all = pd.read_pickle(file)     
    
    return dimension_df_all;
