# -*- coding: utf-8 -*-

from functools import lru_cache
import pandas as pd
import xml.etree.ElementTree as ET
import re

from pynsee.geodata._get_capabilities import _get_capabilities
from pynsee.utils._clean_str import _clean_str

@lru_cache(maxsize=None)
def _get_full_list_wfs(topic, version='2.0.0'):
        
    raw_data_file = _get_capabilities(key=topic, version=version, service='wfs')
        
    root = ET.parse(raw_data_file).getroot()
    
    list_var = ['FeatureTypeList']
    
    find = False
    
    for i in range(len(root)):
        for var in list_var:
            if _clean_str(root[i].tag) == var:
                data = root[i]                
                find = True
                break
        if find: 
            break             
                
    list_df = []
    
    for i in range(len(data)):
        
        df = data[i]
        d = {}
            
        list_var0 = ['Name', 'Title', 'DefaultCRS', 'Abstract']
        list_var1 = ['WGS84BoundingBox', 'Keywords']
        list_subvar = ['LowerCorner', 'UpperCorner', 'Keyword']
        
        for j in range(len(df)):
            
            for var in list_var0:
                if _clean_str(df[j].tag) == var:
                    d[var] = df[j].text
                        
            for var in list_var1:
                if _clean_str(df[j].tag) == var:                    
                    for z in range(len(df[j])):
                        for subvar in list_subvar:
                            if _clean_str(df[j][z].tag) == subvar:
                                d[subvar] = df[j][z].text
        
        df2 = pd.DataFrame(d, index=[0])
            
        list_df.append(df2)
    
    if len(list_df)>0:
        data_all = pd.concat(list_df).reset_index(drop=True).dropna(axis = 0, how = 'all')
    else:
        data_all = list_df

    return data_all
    