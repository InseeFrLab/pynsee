# -*- coding: utf-8 -*-
from functools import lru_cache

@lru_cache(maxsize=None)
def search_insee(pattern = ".*"):
    """Search a pattern among insee series (idbanks)

    Notes: this function uses package's internal data which might not be the most up-to-date.

    Args:
        pattern (str, optional): String used to filter the idbank list. Defaults to ".*", returns all series.

    Examples:
    ---------
    >>> from insee_macrodata import search_insee 
    >>> search_all = search_insee()
    >>> search_paper = search_insee("pâte à papier")
    >>> search_paris = search_insee("PARIS")
    >>> search_survey_gdp = search_insee("Survey|GDP")
    """    
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
