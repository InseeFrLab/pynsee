# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_default_value_siren(msg):
     print(msg)

@lru_cache(maxsize=None)
def _warning_default_value_siret(msg):
     print(msg)

def get_data_from_pattern(pattern, variable = None,
                     kind = "siren", includeHistory = False, number = 20):

    import pandas as pd
    from pynsee.utils._paste import _paste
    from pynsee.sirene.get_data_sirene import get_data_sirene
        
    if kind == 'siren':        
        list_all_variables = ['denominationUniteLegale', 'denominationUsuelle1UniteLegale',
                              'denominationUsuelle2UniteLegale', 'denominationUsuelle3UniteLegale',
                              'nomUniteLegale', 'nomUsageUniteLegale', 'pseudonymeUniteLegale',
                              'prenom1UniteLegale', 'prenom2UniteLegale', 'prenom3UniteLegale',
                              'prenom4UniteLegale', 'prenomUsuelUniteLegale']

        if variable is None:
            variable = ['denominationUniteLegale']
            msg = '!!! By default search is made on the variables:\n{} !!!'.format(_paste(variable, collapse = ' '))
            _warning_default_value_siren(msg)
        else:
            if variable not in list_all_variables:
                string_all_variables = _paste(list_all_variables,collapse= ' ')
                raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
                
    elif kind == 'siret':
        includeHistory = False
        list_all_variables = [ 'libelleCommuneEtablissement', 'libelleVoieEtablissement',
                              'enseigne1Etablissement', 'enseigne2Etablissement', 'enseigne3Etablissement']
        
        if variable is None:
            variable = ['nomUniteLegale']
            msg = '!!! By default search is made on the variables:\n{} !!!'.format(_paste(variable, collapse = ' '))
            _warning_default_value_siret(msg)
        else:
            if variable not in list_all_variables:
                string_all_variables = _paste(list_all_variables, collapse= ' ')
                raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
    else:
         raise ValueError('!!! kind should be among : siren siret !!!')
                    
    list_dataframe = []

    for var in variable:    
    
        if includeHistory:
            search_link = "?q=periode({}.phonetisation:{})&nombre={}".format(var, pattern, number)
        else:
            search_link = "?q={}.phonetisation:{}&champs={}&nombre={}".format(var, pattern, var, number)
                
        df = get_data_sirene(query= search_link, kind = kind)
        list_dataframe.append(df)
        
    data_final = pd.concat(list_dataframe)
    data_final = data_final.reset_index(drop=True)
         
    return(data_final)
    
    