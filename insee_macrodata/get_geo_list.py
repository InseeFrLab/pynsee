# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 15:16:17 2021

@author: eurhope
"""

def get_geo_list(geo):
    
    import requests
    import tempfile
    import pandas as pd
    import xml.etree.ElementTree as ET
    import os
    from tqdm import trange
    
    from ._get_token import _get_token
    
    try:
        proxies = {'http': os.environ['http'],
                   'https': os.environ['https']}
    except:
        proxies = {'http': '','https': ''}
    
    try:
        token = os.environ['insee_token']
    except:
        token = _get_token()
    
    headers = {'Accept': 'application/xml',
           'Authorization': 'Bearer ' + token}
    #geo = communes  arrondissementsMunicipaux arrondissements regions departements
    api_url = 'https://api.insee.fr/metadonnees/V1/geo/' + geo
    results = requests.get(api_url, proxies = proxies, headers=headers)
        
    dirpath = tempfile.mkdtemp()
                            
    raw_data_file = dirpath + '\\' + "raw_data_file"
        
    with open(raw_data_file, 'wb') as f:
        f.write(results.content)
    
    root = ET.parse(raw_data_file).getroot()
        
    n_variable = len(root)
    
    list_data_geo = []
        
    for igeo in trange(n_variable):
        dict_geo = {'Intitule':root[igeo][0].text, #root[igeo][0].tag
                    'Type':root[igeo][1].text, #root[igeo][1].tag
                    'DateCreation':root[igeo][2].text, #root[igeo][2].tag
                    'IntituleSansArticle':root[igeo][3].text,#root[igeo][3].tag
                    }
        data_attrib = pd.DataFrame(root[igeo].attrib, index = [0])
        
        data_geo = pd.DataFrame(dict_geo, index = [0],
                                    columns = ['Intitule', 'Type',
                                               'DateCreation', 'IntituleSansArticle'])
        
        data_geo_all = pd.concat([data_geo, data_attrib], axis=1)
        
        list_data_geo.append(data_geo_all)
        
    
    df_geo = pd.concat(list_data_geo)     
    
    return(df_geo)
