# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 14:11:47 2020

@author: eurhope
"""
# from functools import lru_cache

# @lru_cache(maxsize=None)
def get_idbank_list(*datasets, update = False):
    
    import pandas as pd
    import re
    
    from .get_dataset_list import get_dataset_list 
    from ._get_dataset_metadata import _get_dataset_metadata
    
    insee_dataset = get_dataset_list()    
    insee_dataset_list = insee_dataset['id'].to_list()
    
    for dt in datasets:
        if not dt in insee_dataset_list:               
            raise ValueError("%s is not a dataset from INSEE" % dt)
                
    idbank_list_dataset = []
    
    for dt in datasets:
        idbank_list_dt = _get_dataset_metadata(dt, update = update)
        
        idbank_list_dataset.append(idbank_list_dt)
            
    idbank_list = pd.concat(idbank_list_dataset)
    
    # label columns at the end
    
    r = re.compile(".*_label_.*")
    column_all = idbank_list.columns.to_list()
    column_label = list(filter(r.match, column_all))    
    column_other = [col for col in column_all if col not in column_label]    
    new_column_order = column_other + column_label
    
    idbank_list = pd.DataFrame(idbank_list, columns = new_column_order)
        
    return idbank_list;