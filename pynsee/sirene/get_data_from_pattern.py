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

def get_data_from_pattern(pattern,
                          kind = "siren",
                          variable = None,
                          phonetic_search=False,
                          number = 200,
                          clean=True,
                          activity=True,
                          legal=True):   
    """Get data about companies from a pattern string

    Args:
        pattern (str): the pattern or criterium searched

        kind (str, optional): kind of companies : siren or siret. Defaults to "siren".

        variable (str or list, optional): name of the variable on which the search is applied. Defaults to None.

        phonetic_search (bool, optional): If True phonetic search is triggered, if False the exact string is searched. Defaults to True.
       
        number (int, optional): Maximum number of companies. Defaults to 200.
       
        clean (bool, optional): If True, empty columns are deleted. Defaults to True.
      
        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.

    Raises:
        ValueError: [description]
        ValueError: [description]
        ValueError: [description]
    
    Examples:
        >>> # Get a list of all hospitals in Paris
        >>> df4 = get_data_from_pattern(variable = ["activitePrincipaleUniteLegale", 
        >>>                                        "codePostalEtablissement"],
        >>>                            pattern = ["86.10Z", "75*"], kind = "siret", number = 1000000)
    """        
    if kind == 'siren':        
        # list_all_variables = ['denominationUniteLegale', 'denominationUsuelle1UniteLegale',
        #                       'denominationUsuelle2UniteLegale', 'denominationUsuelle3UniteLegale',
        #                       'nomUniteLegale', 'nomUsageUniteLegale', 'pseudonymeUniteLegale',
        #                       'prenom1UniteLegale', 'prenom2UniteLegale', 'prenom3UniteLegale',
        #                       'prenom4UniteLegale', 'prenomUsuelUniteLegale']

        if variable is None:
            variable = ['denominationUniteLegale']
            msg = '!!! By default search is made on the variables:\n{} !!!'.format(_paste(variable, collapse = ' '))
            _warning_default_value_siren(msg)
        else:
            if type(variable) == str:
                variable = [variable]
            # if not set(variable).issubset(list_all_variables):
            #     string_all_variables = _paste(list_all_variables,collapse= ' ')
            #     raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
                
    elif kind == 'siret':
        # includeHistory = False
        # list_all_variables = ['denominationUniteLegale', 'libelleCommuneEtablissement', 'libelleVoieEtablissement',
        #                       'enseigne1Etablissement', 'enseigne2Etablissement', 'enseigne3Etablissement']
        
        if variable is None:
            # variable = ['nomUniteLegale']
            variable = ['denominationUniteLegale']
            msg = '!!! By default search is made on the variables:\n{} !!!'.format(_paste(variable, collapse = ' '))
            _warning_default_value_siret(msg)
        else:
            if type(variable) == str:
                variable = [variable]
            # if not set(variable).issubset(list_all_variables):
            #     string_all_variables = _paste(list_all_variables, collapse= ' ')
            #     raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
    else:
         raise ValueError('!!! kind should be among : siren siret !!!')
                    
    list_dataframe = []
    
    if phonetic_search:        
        phntc = ".phonetisation"
    else:
        phntc = ""
        
    
    if len(variable) == 1 & len(pattern) == 1:
        variable = variable[0]
        if kind == "siren":
            query = "?q=periode({}{}:{})&nombre={}".format(variable, phntc, pattern, number)        
        else:
            query = "?q={}{}:{}&nombre={}".format(variable, phntc, pattern, number)
    else:       
        list_var_pattern = []
        for var, patt in zip(variable, pattern):
            list_var_pattern.append("{}{}:{}".format(var, phntc, patt))
        query = "?q=" + _paste(list_var_pattern, collapse = " AND ") + "&nombre={}".format(number)
        

    df = get_data_sirene(query = query, kind = kind, 
                         clean=clean, activity=activity, legal=legal)
        
    list_dataframe.append(df)
        
    data_final = pd.concat(list_dataframe)
    data_final = data_final.reset_index(drop=True)
    
        
     # change colummn order        
    if kind == 'siren' :
        first_col = ['siren', 'denominationUniteLegale' ,
                     'dateFin', 'dateDebut', 'categorieEntreprise',
                     'categorieJuridiqueUniteLegale', 'activitePrincipaleUniteLegale']
        
        if set(first_col).issubset(data_final.columns):
            other_col = [col for col in data_final if col not in first_col]
            data_final = data_final[first_col + other_col]
    
   
            
    return(data_final)
    
    