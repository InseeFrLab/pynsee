# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 14:51:04 2021

@author: XLAPDO
"""
from functools import lru_cache

@lru_cache(maxsize=None)
def search_insee(pattern = ".*"):
    
    from ._get_idbank_internal_data_harmonized import _get_idbank_internal_data_harmonized
    from ._get_idbank_internal_data import _get_idbank_internal_data
    
    if not pattern in [".*", ""]:
        idbank_list = _get_idbank_internal_data_harmonized()
        
        pattern = str(pattern).lower()
        
        idbank_selected = idbank_list.loc[
            idbank_list.title_en_lower.str.contains(pattern) |
            idbank_list.title_fr_lower.str.contains(pattern) |
            idbank_list.title_fr_no_accent.str.contains(pattern)]      
        
    else:
        idbank_selected = _get_idbank_internal_data()
    
    idbank_selected = idbank_selected[["nomflow", "idbank", "cleFlow", "title_fr", "title_en"]]
        
    return(idbank_selected)
