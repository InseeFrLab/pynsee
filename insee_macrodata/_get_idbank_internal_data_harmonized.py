# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:35:16 2021

@author: XLAPDO
"""
from functools import lru_cache

@lru_cache(maxsize=None)
def _get_idbank_internal_data_harmonized():
    
    import unidecode
    import pandas as pd
    
    from ._get_idbank_internal_data import _get_idbank_internal_data
    
    idbank_list = _get_idbank_internal_data()
    
    col_selected = ["nomflow", "idbank", "cleFlow", "title_fr", "title_en"]
    idbank_col_selected = idbank_list.columns[idbank_list.columns.isin(col_selected)]
    idbank_list2 = idbank_list[idbank_col_selected]
    
    # all titles in lower case
    title_fr_lower = pd.Series([str(title).lower() for title in idbank_list["title_fr"]])
    idbank_list = idbank_list.assign(title_fr_lower = title_fr_lower.values)
    
    title_en_lower = pd.Series([str(title).lower() for title in idbank_list["title_en"]])
    idbank_list = idbank_list.assign(title_en_lower = title_en_lower.values)
    
    # create column without accent
    title_fr_no_accent = [unidecode.unidecode(str(title)) for title in idbank_list["title_fr_lower"]]
    title_fr_no_accent = pd.Series(title_fr_no_accent)
    idbank_list = idbank_list.assign(title_fr_no_accent = title_fr_no_accent.values)  
    
    return(idbank_list)