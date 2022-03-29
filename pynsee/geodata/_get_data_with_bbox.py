# -*- coding: utf-8 -*-
import os
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd
from pynsee.geodata._geojson_parser import _geojson_parser
from pynsee.geodata._distance import _distance

def _set_global_var(args):

    global link0, list_bbox_full, session
    link0 = args[0]
    list_bbox_full = args[1]

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    

def _get_data_with_bbox2(i):
    link = link0
    list_bbox = list_bbox_full[i]
    return _get_data_with_bbox(link, list_bbox)

def _get_data_with_bbox(link, list_bbox):
        
    # list_bbox = (5.0, 43.0, 6.0, 44.5)
    bounds = [str(b) for b in list_bbox]
    bounds = [bounds[1], bounds[0], bounds[3], bounds[2]]
    BBOX= '&BBOX={}'.format(','.join(bounds)) 
    
    link_query = link + BBOX

    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '', 'https': ''}

    with session.get(link_query, proxies=proxies) as r:                
        data_json = r.json()
    
    if r.status_code == 502:
        time.sleep(1) 
        with session.get(link_query, proxies=proxies) as r:                
            data_json = r.json()
    
    if r.status_code == 502:
        print(f"!!! The following query failed, some data might be missing !!!\n{link_query}")
        return pd.DataFrame()
        
    if 'features' in data_json.keys():
        
        json = data_json['features']      
        
        if len(json) > 0:      
               
            if len(json) == 1000:
                # data limit reached
                # data searched relaunch with a smaller bbox
                # bbox area (longitude) divided by two
                
                width = _distance((list_bbox[0], list_bbox[1]), (list_bbox[2], list_bbox[1]))
                height = _distance((list_bbox[0], list_bbox[1]), (list_bbox[0], list_bbox[3]))
             
                if width > height:
                    list_bbox1 = [list_bbox[0], list_bbox[1],
                                  (list_bbox[2]+list_bbox[0])/2, list_bbox[3]]
                    
                    list_bbox2 = [(list_bbox[2]+list_bbox[0])/2, list_bbox[1],
                                  list_bbox[2], list_bbox[3]]
                else:
                    list_bbox1 = [list_bbox[0], list_bbox[1],
                                  list_bbox[2], (list_bbox[1]+list_bbox[3])/2]
                    
                    list_bbox2 = [list_bbox[0], (list_bbox[1]+list_bbox[3])/2,
                                  list_bbox[2], list_bbox[3]]
                    
                
                df1 = _get_data_with_bbox(link, list_bbox1)
                
                df2 = _get_data_with_bbox(link, list_bbox2)
                
                data_final = pd.concat([df1, df2]).reset_index(drop=True) 
            else:            
                # data limit not reached
                data_final = _geojson_parser(json).reset_index(drop=True)
                
        else:
            # no data found, return empty dataframe
            data_final = pd.DataFrame()
    else:
        # no data found, return empty dataframe
        data_final = pd.DataFrame()
            
    return data_final
    