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
    
    return(df_geo)
