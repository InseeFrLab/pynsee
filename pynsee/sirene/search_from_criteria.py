# -*- coding: utf-8 -*-

import pandas as pd
import re
from pynsee.utils._paste import _paste
from pynsee.sirene._get_data_sirene import _get_data_sirene

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_default_value_siren(msg):
     print(msg)

@lru_cache(maxsize=None)
def _warning_default_value_siret(msg):
     print(msg)

def search_from_criteria(          
                          variable,
                          pattern,  
                          kind = "siren",
                          phonetic_firstvar=False,
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

        phonetic_firstvar (bool, optional): If True phonetic search is triggered on the first variable of the list, if False the exact string is searched. Defaults to True.
       
        number (int, optional): Maximum number of companies. Defaults to 200.
       
        clean (bool, optional): If True, empty columns are deleted. Defaults to True.
      
        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.
    
    Examples:
        >>> # Get a list of hospitals in Paris
        >>> df = search_from_criteria(variable = ["activitePrincipaleUniteLegale", 
        >>>                                        "codePostalEtablissement"],
        >>>                             pattern = ["86.10Z", "75*"], kind = "siret")
        >>>
        >>> # Get a list of companies located in Igny city whose name matches with 'pizza' using a phonetic search
        >>> df = search_from_pattern(variable = ["libelleCommuneEtablissement",
        >>>                            'denominationUniteLegale'],
        >>>                 pattern = ["igny", 'pizza'], 
        >>>                 phonetic_firstvar=True, kind = "siret")
        >>>
        >>> # Get a list of companies whose name matches with 'SNCF' (French national railway company) 
        >>> # and whose legal status is SAS (societe par actions simplifiee)
        >>> df = search_from_criteria(variable=["denominationUniteLegale",
        >>>                                       'categorieJuridiqueUniteLegale'],                                     
        >>>                                       pattern=["sncf", '5710'], kind="siren")
        >>>
        >>> # Get data on Hadrien Leclerc
        >>> df = search_from_criteria(variable = ['prenom1UniteLegale', 'nomUniteLegale'],
        >>>                             pattern = ['hadrien', 'leclerc'],
        >>>                             kind = 'siret', only_alive = False)
    """        
    if (not kind == 'siret') & (not kind == 'siren') :      
        raise ValueError('!!! kind should be among : siren, siret !!!')
                        
     

    if type(variable) == str:
        variable = [variable] 

    if type(pattern) == str:
        pattern = [pattern] 
        
    list_siren_hist_variable = [
                                'nomUniteLegale', 
                                'nomUsageUniteLegale',
                                'denominationUniteLegale',
                                'denominationUsuelle1UniteLegale',
                                'denominationUsuelle2UniteLegale',
                                'denominationUsuelle3UniteLegale',
                                'categorieJuridiqueUniteLegale',                                
                                'etatAdministratifUniteLegale'
                                'nicSiegeUniteLegale',
                                'activitePrincipaleUniteLegale',
                                'caractereEmployeurUniteLegale',
                                'economieSocialeSolidaireUniteLegale',
                                'nomenclatureActivitePrincipaleUniteLegale'
                                ]
    
    list_siret_hist_variable = ['denominationUsuelleEtablissement',
                                'enseigne1Etablissement',
                                'enseigne2Etablissement',
                                'enseigne3Etablissement',
                                'activitePrincipaleEtablissement',
                                'etatAdministratifEtablissement',
                                'nomenclatureActiviteEtablissement',
                                'caractereEmployeurEtablissement']
    
    if kind == 'siren':
        list_hist_variable = list_siren_hist_variable
    else:
        list_hist_variable = list_siret_hist_variable
        
    list_var_pattern = []
    
    for var, patt in zip(variable, pattern):
        
        phntc = ""  
        if var == variable[0]:
             if phonetic_firstvar:        
                 phntc = ".phonetisation"
                 
        #if pattern has several words, split and put mutiple conditions with OR
        list_patt = patt.split(' ')
        
        list_var_patt = []
        for ptt in list_patt:
            if var in list_hist_variable:
                list_var_patt.append("periode({}{}:{})".format(var, phntc, ptt))
            else:
                list_var_patt.append("{}{}:{}".format(var, phntc, ptt))
        
        list_var_pattern.append(_paste(list_var_patt, collapse = " OR "))
        
    query = "?q=" + _paste(list_var_pattern, collapse = " AND ") + "&nombre={}".format(number)


    df = _get_data_sirene(query = query, kind = kind, 
                         clean=clean, activity=activity,
                         legal=legal, only_alive=only_alive)
    
    if not df is None:
        df = df.reset_index(drop=True)
            
    return(df)
    
    