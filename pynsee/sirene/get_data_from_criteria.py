# -*- coding: utf-8 -*-

import pandas as pd
from pynsee.utils._paste import _paste
from pynsee.sirene.get_data_sirene import get_data_sirene

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_default_value_siren(msg):
     print(msg)

@lru_cache(maxsize=None)
def _warning_default_value_siret(msg):
     print(msg)

def get_data_from_criteria(          
                          variable,
                          pattern,  
                          kind = "siren",
                          phonetic_search=False,
                          number = 1000000,
                          clean=True,
                          activity=True,
                          legal=True,
                          only_alive=True):   
    """Get data about companies from criteria on variables

    Args:
        pattern (str): the pattern or criterium searched

        kind (str, optional): kind of companies : siren or siret. Defaults to "siren".

        variable (str or list, optional): name of the variable on which the search is applied. Defaults to None.

        phonetic_search (bool, optional): If True phonetic search is triggered, if False the exact string is searched. Defaults to True.
       
        number (int, optional): Maximum number of companies. Defaults to 200.
       
        clean (bool, optional): If True, empty columns are deleted. Defaults to True.
      
        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.
    
    Examples:
        >>> # Get a list of all hospitals in Paris
        >>> df = get_data_from_criteria(variable = ["activitePrincipaleUniteLegale", 
        >>>                                        "codePostalEtablissement"],
        >>>                             pattern = ["86.10Z", "75*"], kind = "siret")
        >>>
        >>> # Get a list of companies located in Igny city whose name matches with 'pizza' using a phonetic search
        >>> df = get_data_from_pattern(variable = ["libelleCommuneEtablissement",
        >>>                            'denominationUniteLegale'],
        >>>                 pattern = ["igny", 'pizza'], 
        >>>                 phonetic_search=True, kind = "siret")

    """        
    if (not kind == 'siret') & (not kind == 'siren') :      
        raise ValueError('!!! kind should be among : siren siret !!!')
                        
    if phonetic_search:        
        phntc = ".phonetisation"
    else:
        phntc = ""    

    if type(variable) == 'str':
        variable = [variable] 

    if type(pattern) == 'str':
        pattern = [pattern] 

    list_var_pattern = []
    for var, patt in zip(variable, pattern):
        list_var_pattern.append("{}{}:{}".format(var, phntc, patt))

    query = "?q=" + _paste(list_var_pattern, collapse = " AND ") + "&nombre={}".format(number)

    # if len(variable) == 1 & len(pattern) == 1:
    #     variable = variable[0]
    #     if kind == "siren":
    #         query = "?q=periode({}{}:{})&nombre={}".format(variable, phntc, pattern, number)        
    #     else:
    #         query = "?q={}{}:{}&nombre={}".format(variable, phntc, pattern, number)
    # else:       
    #     list_var_pattern = []
    #     for var, patt in zip(variable, pattern):
    #         list_var_pattern.append("{}{}:{}".format(var, phntc, patt))
    #     query = "?q=" + _paste(list_var_pattern, collapse = " AND ") + "&nombre={}".format(number)
        

    df = get_data_sirene(query = query, kind = kind, 
                         clean=clean, activity=activity,
                         legal=legal, only_alive=only_alive)
        
    df = df.reset_index(drop=True)
            
    return(df)
    
    