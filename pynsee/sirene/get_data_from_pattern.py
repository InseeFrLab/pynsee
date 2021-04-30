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

def get_data_from_pattern(pattern, variable = None,
                     kind = "siren", includeHistory = False, number = 20):   
        
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
            if type(variable) == str:
                variable = [variable]
            if not set(variable).issubset(list_all_variables):
                string_all_variables = _paste(list_all_variables,collapse= ' ')
                raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
                
    elif kind == 'siret':
        includeHistory = False
        list_all_variables = ['libelleCommuneEtablissement', 'libelleVoieEtablissement',
                              'enseigne1Etablissement', 'enseigne2Etablissement', 'enseigne3Etablissement']
        
        if variable is None:
            variable = ['nomUniteLegale']
            msg = '!!! By default search is made on the variables:\n{} !!!'.format(_paste(variable, collapse = ' '))
            _warning_default_value_siret(msg)
        else:
            if type(variable) == str:
                variable = [variable]
            if not set(variable).issubset(list_all_variables):
                string_all_variables = _paste(list_all_variables, collapse= ' ')
                raise ValueError('!!! variable should be among : {} !!!'.format(string_all_variables))
    else:
         raise ValueError('!!! kind should be among : siren siret !!!')
                    
    list_dataframe = []

    for var in variable:    
#        var='denominationUniteLegale'
#        if includeHistory:
#            query = "?q=periode({}.phonetisation:{})&nombre={}".format(var, pattern, number)
#        else:
##            query = "?q={}.phonetisation:{}&champs={}&nombre={}".format(var, pattern, var, number)
#            query = "?q={}.phonetisation:{}&nombre={}".format(var, pattern, number)
#
        if kind == "siren":
            query = "?q=periode({}.phonetisation:{})&nombre={}".format(var, pattern, number)        
        else:
            query = "?q={}.phonetisation:{}&nombre={}".format(var, pattern, number)
            query = "?q={}.phonetisation:{}&champs={}&nombre={}".format(var, pattern, var, number)
            
        df = get_data_sirene(query = query, kind = kind)
        
        list_dataframe.append(df)
        
    data_final = pd.concat(list_dataframe)
    data_final = data_final.reset_index(drop=True)
    
     # change col order
    list_all_na_col = [col for col in data_final.columns if all(pd.isna(data_final[col]))]
    list_first_col = [col for col in data_final.columns if col not in list_all_na_col]
    data_final = data_final[list_first_col + list_all_na_col]
    
    if kind == 'siren' :
        first_col = ['siren', 'denominationUniteLegale' ,
                     'dateFin', 'dateDebut', 'categorieEntreprise',
                     'categorieJuridiqueUniteLegale', 'activitePrincipaleUniteLegale']
        
        if set(first_col).issubset(data_final.columns):
            other_col = [col for col in data_final if col not in first_col]
            data_final = data_final[first_col + other_col]
        
    return(data_final)
    
    