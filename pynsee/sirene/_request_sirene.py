# Copyright : INSEE, 2021

import pandas as pd
import math
from functools import lru_cache

from pynsee.utils._request_insee import _request_insee
from pynsee.sirene._make_dataframe import _make_dataframe

@lru_cache(maxsize=None)
def _request_sirene(query, kind, number):
    
    if kind == 'siren':        
        main_key = 'unitesLegales'
    elif kind == 'siret':
        main_key = 'etablissements'
    else:
        raise ValueError('!!! kind should be among : siren siret !!!')

    INSEE_api_sirene_siren = "https://api.insee.fr/entreprises/sirene/V3"
    number_query_limit = 1000

    number_query = min(number_query_limit, number)
    
    n_query_total = math.ceil(number / number_query_limit)    
    i_query = 1
    query_number = '{}/{}'.format(i_query, n_query_total)
    
    main_query = INSEE_api_sirene_siren + '/' + kind + query

    link = main_query +  "&nombre={}".format(number_query)
    
    if number > number_query_limit:
        link = link + '&curseur=*'

    request = _request_insee(api_url = link, file_format = 'application/json;charset=utf-8')
    
    list_dataframe = []
    
    request_status = request.status_code
    
    if request_status == 200:
        
        data_request = request.json()
        
        data_request_1 = _make_dataframe(data_request, main_key, '1')
        df_nrows = len(data_request_1[kind].unique())
        
        list_dataframe.append(data_request_1)       
               
        list_header_keys = list(data_request['header'].keys())
        
        if 'curseur' in list_header_keys:
        
            cursor = data_request['header']['curseur']
            following_cursor = data_request['header']['curseurSuivant']
            
            while (following_cursor != cursor) & (request_status == 200) & (number < df_nrows):
                
                i_query += 1
                query_number = '{}/{}'.format(i_query, n_query_total)
            
                new_query = main_query + following_cursor + "&nombre={}".format(number_query_limit)
                
                request_new = _request_insee(api_url=new_query, file_format= 'application/json;charset=utf-8')
                
                request_status = request_new.status_code                               
            
                if request_status == 200:
                    
                    data_request = request.json()
                    cursor = data_request['header']['curseur']
                    following_cursor = data_request['header']['curseurSuivant']
                    
                    if len(data_request[main_key]) > 0:
                    
                        df = _make_dataframe(data_request, main_key, query_number)
                        df_nrows += len(df[kind].unique())
                        list_dataframe.append(df)
            
    
        data_final = pd.concat(list_dataframe)
        
        return(data_final)     
    else:        
        print(request.text)
        return(None)