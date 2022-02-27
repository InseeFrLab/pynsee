# -*- coding: utf-8 -*-

import sys
import time
import pandas as pd
import requests
import os
import multiprocessing
import tqdm 
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib2 import Path

from pynsee.geodata.GeoDataframe import GeoDataframe
    
from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.geodata._get_bbox_list import _get_bbox_list
from pynsee.geodata._get_data_with_bbox import _get_data_with_bbox2
from pynsee.geodata._get_data_with_bbox import _set_global_var
from pynsee.geodata._geojson_parser import _geojson_parser
from pynsee.geodata.get_geodata_list import get_geodata_list

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def get_geodata(id,
            polygon=None,
            update=False):
    """Get geographical data from an identifier and IGN API

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')
    """            
          
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
    file_name = insee_folder + '/' +  _hash(link) 

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        home = str(Path.home())
        user_agent = os.path.basename(home)
    except:
        user_agent = ""

    headers = {'User-Agent': 'python_package_pynsee_' + user_agent.replace("/", "")}

    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '', 'https': ''}
    
    if (not os.path.exists(file_name)) | (update is True):

        data = session.get(link, proxies=proxies, headers=headers)

        if data.status_code == 502:
            time.sleep(1) 
            data = session.get(link, proxies=proxies, headers=headers)
        
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

            Nprocesses = min(6, multiprocessing.cpu_count())
            
            args = [link0, list_bbox]
            irange = range(len(list_bbox))

            with multiprocessing.Pool(initializer= _set_global_var,
                                    initargs=(args,),
                                    processes=Nprocesses) as pool:

                list_data = list(tqdm.tqdm(pool.imap(_get_data_with_bbox2, irange),
                                        total=len(list_bbox)))
                            
            data_all = pd.concat(list_data).reset_index(drop=True) 

        elif len(json) != 0:

            data_all = _geojson_parser(json).reset_index(drop=True)

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
        except:
            os.remove(file_name)
            data_all_clean = get_geodata(id=id,
                                      polygon=polygon,
                                      update=True)
        else:
            _warning_cached_data(file_name)
    
    # get crs for id
    # disable/enable print vefore/after get_geodata_list use
    sys.stdout = open(os.devnull, 'w')
    geodata_list = get_geodata_list()
    sys.stdout = sys.__stdout__

    crs = geodata_list.loc[geodata_list["Identifier"]== id, "DefaultCRS"].iloc[0]
    crs = crs.replace("urn:ogc:def:crs:", "").replace("::", ":")
    data_all_clean["crs"] = crs
    
    data_all_clean = GeoDataframe(data_all_clean)
        
    return data_all_clean

