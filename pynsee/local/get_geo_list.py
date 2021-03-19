# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def get_geo_list(geo):    
    """Get a list of French geographic areas (communes, departements, regions ...)

    Args:
        geo (str): choose among : 'communes', 'regions', 'departements',
                          'arrondissements', 'arrondissementsMunicipaux'

    Raises:
        ValueError: geo should be among the geographic area list
    
    Examples:
    ---------
    >>> city_list = get_geo_list('communes')
    >>> region_list = get_geo_list('regions')
    >>> departement_list = get_geo_list('departements')
    """   
    import tempfile
    import pandas as pd
    import xml.etree.ElementTree as ET
    from tqdm import trange
    
    from pynsee.utils._request_insee import _request_insee
    from pynsee.utils._paste import _paste
    
    list_available_geo = ['communes', 'regions', 'departements',
                          'arrondissements', 'arrondissementsMunicipaux']
    geo_string = _paste(list_available_geo, collapse = " ")
    
    if not geo in list_available_geo:
        msg = "!!! geo is not available\nPlease choose geo among:\n%s" % geo_string
        raise ValueError(msg)
     
    api_url = 'https://api.insee.fr/metadonnees/V1/geo/' + geo
    results = _request_insee(api_url=api_url, sdmx_url=None)
        
    dirpath = tempfile.mkdtemp()
                            
    raw_data_file = dirpath + '\\' + "raw_data_file"
        
    with open(raw_data_file, 'wb') as f:
        f.write(results.content)
    
    root = ET.parse(raw_data_file).getroot()
        
    n_variable = len(root)
    
    list_data_geo = []
        
    for igeo in trange(n_variable, desc = "Getting %s" % geo):

        n_var = len(root[igeo])
        
        dict_geo = {}
        
        for ivar in range(n_var):
            dict_geo[root[igeo][ivar].tag] = root[igeo][ivar].text
               
        dict_geo = {**dict_geo, **root[igeo].attrib}

        data_geo = pd.DataFrame(dict_geo, index = [0])
        
        list_data_geo.append(data_geo)        
    
    df_geo = pd.concat(list_data_geo)   
    df_geo.columns = ['TITLE', 'TYPE', 'DATECREATION', 'TITLE_SHORT', 'CODE', 'URI']
    
    if geo in ['communes', 'arrondissements', 'arrondissementsMunicipaux']:
        dep = get_geo_list('departements')
        dep_short = dep[['CODE', 'TITLE']]
        dep_short.columns = ['CODE', 'TITLE_DEP1']
        
        dep_short2 = dep[['CODE', 'TITLE']]
        dep_short2.columns = ['CODE', 'TITLE_DEP2']
        
        df_geo = df_geo.assign(code_dep1 = df_geo['code'].str[:2],
                               code_dep2 = df_geo['code'].str[:3])
        
        df_geo = df_geo.merge(dep_short, how = 'left', left_on = 'code_dep1', right_on = 'CODE')
        df_geo = df_geo.merge(dep_short2, how = 'left', left_on = 'code_dep2', right_on = 'CODE')
        
        for i in range(len(df_geo.index)):  
            if pd.isna(df_geo.loc[i, 'TITLE_DEP1']):
                df_geo.loc[i, 'CODE_DEP'] = df_geo.loc[i, 'code_dep2']
                df_geo.loc[i, 'TITLE_DEP'] = df_geo.loc[i, 'TITLE_DEP2']
            else:
                df_geo.loc[i, 'CODE_DEP'] = df_geo.loc[i, 'code_dep1']
                df_geo.loc[i, 'TITLE_DEP'] = df_geo.loc[i, 'TITLE_DEP1']    
      
    
    return(df_geo)
