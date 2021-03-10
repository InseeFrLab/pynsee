# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _get_geo_relation(geo, code, relation):    
   
    # relation_list = ['ascendants', 'descendants', 'suivants', 'precedents', 'projetes']
    # list_available_geo = ['communes', 'regions', 'departements',
    #                       'arrondissements', 'arrondissementsMunicipaux']
    # code = '11'
    # geo = 'region'
    # relation = 'descendants'

    #idf = _get_geo_relation('region', "11", 'descendants')
    #essonne = _get_geo_relation('region', "11", 'ascendants')
    import os, requests
    import tempfile
    import pandas as pd
    import xml.etree.ElementTree as ET
    from tqdm import trange

    from pynsee.utils._request_insee import _request_insee

    api_url = 'https://api.insee.fr/metadonnees/V1/geo/' + geo + '/' + code + '/' + relation
    
    results = _request_insee(api_url = api_url)
    
    dirpath = tempfile.mkdtemp()
                            
    raw_data_file = dirpath + '\\' + "raw_data_file"
        
    with open(raw_data_file, 'wb') as f:
        f.write(results.content)
    
    root = ET.parse(raw_data_file).getroot()
    
    n_geo = len(root)
    
    list_geo_relation = []
    
    for igeo in trange(n_geo):
        n_var = len(root[igeo])
        
        dict_var = {}
        
        for ivar in range(n_var):
            dict_var[root[igeo][ivar].tag] = root[igeo][ivar].text
       
        dict_var = {**dict_var, **root[igeo].attrib}
        df_relation = pd.DataFrame(dict_var, index=[0])    
        list_geo_relation.append(df_relation)
    
    df_relation_all = pd.concat(list_geo_relation)
    df_relation_all = df_relation_all.assign(geo_init = code)
    
    return(df_relation_all)