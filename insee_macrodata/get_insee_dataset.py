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
    from .get_insee import get_insee 
    from .get_dataset_list import get_dataset_list 
    
    insee_dataset = get_dataset_list()    
    insee_dataset_list = insee_dataset['id'].to_list()
    
    # check if the dataset exists in INSEE's list
    if not dataset in insee_dataset_list:               
        raise ValueError("%s is not a dataset from INSEE" % dataset)    
            
    INSEE_sdmx_link_idbank = "https://bdm.insee.fr/series/sdmx/data/"
        
    query = INSEE_sdmx_link_idbank + dataset
    
    if filter is not None:
        query = query + "/" + str(filter)
    
    parameters = ["startPeriod", "endPeriod",
                  "firstNObservations", "lastNObservations", "updatedAfter"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))
    
    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse = '&')
        query = query + added_param_string            
    
    data = get_insee(query)
    
    return data;