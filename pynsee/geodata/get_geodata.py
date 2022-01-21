# -*- coding: utf-8 -*-

import pandas as pd
import requests
import os
import math
import multiprocessing
import tqdm 
import shapely.wkt

from pynsee.geodata.GeoDataframe import GeoDataframe
    
from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.geodata._get_bbox_list import _get_bbox_list
from pynsee.geodata._get_data_with_bbox import _get_data_with_bbox
from pynsee.geodata._geojson_parser import _geojson_parser

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def get_geodata(id,
            polygon=None,
            update=False):
       
    # topic = 'administratif'
    # id = 'ADMINEXPRESS-COG-CARTO.LATEST:commune'
    # id = 'LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:departement'
   
    topic = "administratif"
    service = 'WFS'
    Version = "2.0.0"
        
    # make the query link for ign
    geoportail = 'https://wxs.ign.fr/{}/geoportail'.format(topic)
    Service = 'SERVICE=' + service + '&'
    version = 'VERSION=' + Version + '&'
    request = 'REQUEST=GetFeature&'
    typename = 'TYPENAME=' + id + '&'
        
    link0 = geoportail + '/wfs?' + Service + version + request + typename \
               + 'OUTPUTFORMAT=application/json&COUNT=1000' 
    
    # add bounding box to link if polygon provided
    if polygon is not None:
        bounds = polygon.bounds
        bounds = [str(b) for b in bounds]
        bounds = [bounds[1], bounds[0], bounds[3], bounds[2]]
        BBOX= '&BBOX={}'.format(','.join(bounds)) 
        link = link0 + BBOX
    else:
        link = link0
            
    insee_folder = _create_insee_folder()
    file_name = insee_folder + '/' +  _hash(link) + ".csv"       
    
    if (not os.path.exists(file_name)) | (update is True):

        data = requests.get(link)
        
        if data.status_code != 200:
            print('Query:\n%s' % link)
            print(data)
            print(data.text)
            return pd.DataFrame({'status':data.status_code,
                                'comment':data.text}, index=[0])

        data_json = data.json()
        
        json = data_json['features']
                
        # if maximum reached
        # split the query with the bouding box list
        if len(json) == 1000:
            
            list_bbox = _get_bbox_list(polygon=polygon,
                                       update=update)

            list_data = []
            for i in tqdm.trange(len(list_bbox)):                
                df = _get_data_with_bbox(link=link0, list_bbox=list_bbox[i])
                list_data.append(df)
                
            data_all = pd.concat(list_data).reset_index(drop=True) 

        elif len(json) != 0:

            data_all = _geojson_parser(json)

        else:
            msg = '!!! Query is correct but no data found !!!'
            print(msg)
            return pd.DataFrame({'status': 200, 'comment': msg}, index=[0])
        
        # drop duplicates
        data_col = data_all.columns

        if 'geometry' in data_col:
            
            selected_col = [col for col in data_col if col not in ['geometry', 'bbox']]
            data_all_clean = data_all[selected_col].drop_duplicates()
            
            row_selected = [int(i) for i in data_all_clean.index]
            geom = data_all.loc[row_selected, 'geometry']
            data_all_clean['geometry'] = geom
            
            if 'bbox' in data_col:
                geom = data_all.loc[row_selected, 'bbox']
                data_all_clean['bbox'] = geom
                
            data_all_clean = data_all_clean.reset_index(drop=True)

        else:
            data_all_clean = data_all.drop_duplicates()

        # drop data outside polygon
        if polygon is not None:
            row_selected = []
            for i in range(len(data_all_clean)):
                geom = data_all_clean.loc[i,'geometry']
                if geom.intersects(polygon):
                    row_selected.append(i)
            if len(row_selected) > 0:
                data_all_clean = data_all_clean.loc[row_selected,:]
            
        data_all_clean = data_all_clean.reset_index(drop=True)
        
        data_all_clean.to_pickle(file_name)
        print("Data saved: {}".format(file_name))
    else:        
        try:
            data_all_clean = pd.read_pickle(file_name)
                
            data_all_clean = pd.read_pickle(file_name)
        except:
            os.remove(file_name)
            data_all_clean = get_geodata(id=id,
                                      polygon=polygon,
                                      update=True)
        else:
            _warning_cached_data(file_name)
    
    data_all_clean = GeoDataframe(data_all_clean)
    
    return data_all_clean

