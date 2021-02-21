# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 23:36:31 2020

@author: eurhope
"""

def get_insee_idbank(*idbanks,
                     startPeriod = None,
                     endPeriod = None,
                     firstNObservations = None,
                     lastNObservations = None,
                     includeHistory = None,
                     updatedAfter = None):
    
    import pandas
    import math
    
    from ._get_insee import _get_insee  
    from ._paste import _paste  
            
    INSEE_sdmx_link_idbank = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/"
    INSEE_api_link_idbank = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/"
        
    # 
    # create the parameters to be added to the query
    # 
    
    parameters = ["startPeriod", "endPeriod",
                  "firstNObservations", "lastNObservations", "updatedAfter"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))
    
    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse = '&')
        
    # 
    # make one single list of idbanks
    # 
    
    list_idbank = []
    
    for id in range(len(idbanks)):    
        if isinstance(idbanks[id], list):    
            list_idbank = list_idbank + idbanks[id]
        elif isinstance(idbanks[id], pandas.core.series.Series):
            list_idbank = list_idbank + idbanks[id].to_list()
        elif isinstance(idbanks[id], str):
            list_idbank = list_idbank + [idbanks[id]]
        else:
            list_idbank = list_idbank + [idbanks[id]]
    
    # 
    # create the ranges of the queries
    # mutliple queries will be created each with 400 idbanks
    #
    
    n_idbank = len(list_idbank)
    idbank_limit = 400
    max_seq_idbank = math.ceil(n_idbank/idbank_limit)
        
    list_data = []
    
    for q in range(max_seq_idbank):
          
        min_range = q * idbank_limit
        max_range = min((q + 1) * idbank_limit, n_idbank + 1) 
        
        list_idbank_q = list_idbank[min_range:max_range]  
         
        sdmx_query = INSEE_sdmx_link_idbank + _paste(list_idbank_q, collapse = '+') 
        api_query = INSEE_api_link_idbank + _paste(list_idbank_q, collapse = '+')  
        
        if len(list_addded_param) > 0:
             sdmx_query = sdmx_query + added_param_string
             api_query = api_query + added_param_string
             
        list_data.append(_get_insee(api_query=api_query,
                                    sdmx_query=sdmx_query,
                                    step =  str("{0}/{1}").format(q+1, max_seq_idbank)))
    
    data = pandas.concat(list_data)
    
    return data