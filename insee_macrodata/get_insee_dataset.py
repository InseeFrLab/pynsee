# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 23:36:31 2020

@author: eurhope
"""

def get_insee_dataset(dataset,
                      filter = None,
                      startPeriod = None,
                      endPeriod = None,
                      firstNObservations = None,
                      lastNObservations = None,
                      includeHistory = None,
                      updatedAfter = None):
    
    from ._paste import _paste 
    from ._get_insee import _get_insee 
    from .get_dataset_list import get_dataset_list 
    
    insee_dataset = get_dataset_list()    
    insee_dataset_list = insee_dataset['id'].to_list()
    
    # check if the dataset exists in INSEE's list
    if not dataset in insee_dataset_list:               
        raise ValueError("%s is not a dataset from INSEE" % dataset)    
            
    INSEE_sdmx_link_idbank = "https://bdm.insee.fr/series/sdmx/data/"
    INSEE_api_link_idbank = "https://bdm.insee.fr/series/sdmx/data/"
       
    sdmx_query = INSEE_sdmx_link_idbank + dataset
    api_query = INSEE_api_link_idbank + dataset
    
    if filter is not None:
        sdmx_query = sdmx_query + "/" + str(filter)
        api_query = api_query + "/" + str(filter)
    
    parameters = ["startPeriod", "endPeriod",
                  "firstNObservations", "lastNObservations", "updatedAfter"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))
    
    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse = '&')
        sdmx_query = sdmx_query + added_param_string 
        api_query = api_query + added_param_string            
    
    data = _get_insee(api_query=api_query, sdmx_query=sdmx_query)
    
    return data