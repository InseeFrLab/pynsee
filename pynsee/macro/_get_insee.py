# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 20:06:49 2020

@author: eurhope
"""
from functools import lru_cache

@lru_cache(maxsize=None)
def _get_insee(api_query, sdmx_query, step = "1/1"):
    
    import tempfile
    import pandas as pd
    import os
    import xml.dom.minidom
    from tqdm import trange
    
    from ._get_date import _get_date
    from ._request_insee import _request_insee
    
    # "001694056", "001691912", "001580062", "001688370", "010565692"
    # sdmx_query = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
    # api_query = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
    # create temporary directory
    dirpath = tempfile.mkdtemp()
                        
    # results = requests.get(query, proxies = proxies) 
    results = _request_insee(api_url=api_query, sdmx_url=sdmx_query)
        
    raw_data_file = dirpath + '\\' + "raw_data_file"
        
    with open(raw_data_file, 'wb') as f:
        f.write(results.content)
    
    # parse the xml file
    root = xml.dom.minidom.parse(raw_data_file)
        
    # delete the file
    if os.path.exists(raw_data_file):
        os.remove(raw_data_file)    
    
    n_series = len(root.getElementsByTagName("Series"))
    
    # 
    # for all series, observations and attributes (depending on time) 
    # collect the data (3 loops)
    # 
    
    list_series = []
        
    for j in trange(n_series, desc = "%s - Getting series" % step):
        
        data = root.getElementsByTagName("Series")[j]        
            
        n_obs = len(data.getElementsByTagName("Obs"))
        
        # 
        # collect the obsevation values from the series
        # 
        
        list_obs = []
        #trange(n_obs, desc = "2nd loop - Collecting observations")
        #range(n_obs)
        for i in range(n_obs):
        
            obs = data.getElementsByTagName("Obs")[i]._attrs
                    
            dict_obs = {}
            for a in obs:
               dict_obs[a] = obs[a]._value
            
            col = list(dict_obs.keys())
                    
            df = pd.DataFrame(dict_obs, columns = col, index=[0])
            
            list_obs.append(df)
        
        obs_series = pd.concat(list_obs)
        
        # 
        # collect attributes values from the series 
        # 
        
        attr_series = data._attrs
        
        dict_attr = {}
        for a in attr_series:
           dict_attr[a] = attr_series[a]._value
        
        col_attr = list(dict_attr.keys())
        attr_series = pd.DataFrame(dict_attr, columns = col_attr, index=[0])
        
        data_series = pd.concat([obs_series, attr_series], axis=1)
        
        # 
        # add date column
        # 
        
        freq = attr_series.FREQ[0]
        time_period = obs_series.TIME_PERIOD.to_list()
        
        dates = _get_date(freq, time_period)    
        # new column
        data_series = data_series.assign(DATE = dates) 
        # place DATE column in the first position
        data_series = data_series[['DATE'] + [c for c in data_series if c not in ['DATE']]]
        
        # append series dataframe to final list
        list_series.append(data_series)
        
    data_final = pd.concat(list_series)
    
    # index and sort dataframe by date
    data_final = data_final.set_index('DATE')
    data_final = data_final.sort_values(["IDBANK", "DATE"])
        
    #harmonise column names
    colnames = data_final.columns
    replace_hyphen = lambda x: str(x).replace("-", "_")
    newcolnames = list(map(replace_hyphen, colnames))
    data_final.columns = newcolnames
    
    data_final["OBS_VALUE"] = data_final["OBS_VALUE"].apply(pd.to_numeric, errors='coerce')
    
    print('Data has been cached\n')  
        
    return data_final
