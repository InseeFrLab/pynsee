# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 15:42:56 2020

@author: eurhope
"""
from functools import lru_cache

@lru_cache(maxsize=None)
def get_dataset_list() :
    
    import requests
    import tempfile
    import xml.etree.ElementTree as ET
    import pandas as pd
    import os
    
    INSEE_sdmx_link_dataflow = "https://bdm.insee.fr/series/sdmx/dataflow"
    
    proxies = {
     'http': os.environ.get('http'),
     'https': os.environ.get('https'),
    }
    
    results = requests.get(INSEE_sdmx_link_dataflow, proxies = proxies)
    
    # create temporary directory
    dirpath = tempfile.mkdtemp()
    
    dataflow_file = dirpath + '\\dataflow_file'
    
    with open(dataflow_file, 'wb') as f:
        f.write(results.content)
    
    root = ET.parse(dataflow_file).getroot()
    
    data = root[1][0]
        
    n_dataflow = len(data)
    
    list_df = []
    
    for i in range(0, n_dataflow):
            
        dataset = {'id': [next(iter(data[i].attrib.values()))],
                   'Name.fr': [data[i][1].text],
                   'Name.en': [data[i][2].text],
                   'url': [data[i][0][0][0].text],
                   'n_series': [data[i][0][1][0].text]
                }
    
        dt = pd.DataFrame(dataset, columns = ['id', 'Name.fr', 'Name.en',
                                              'url', 'n_series'])
        list_df.append(dt)    
            
    # concatenate list of dataframes
    df = pd.concat(list_df)
    
    # clean up columns
    df = df.astype(str)
    
    df['n_series'] = df['n_series'].str.replace('\D', '', regex=True)
    df['n_series'] = df['n_series'].astype('int')
    
    df = df[df["id"] != "SERIES_BDM"]
    
    df["Name.en"] = df["Name.en"].str.replace('^\\n\s{0,}', '', regex=True)
    df["Name.fr"] = df["Name.fr"].str.replace('^\\n\s{0,}', '', regex=True)
    
    df = df[df["Name.en"] != ""]
    df = df[df["Name.fr"] != ""]
    
    return df;
