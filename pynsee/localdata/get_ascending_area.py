# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:52:54 2023

@author: thomas.grandjean@developpement-durable.gouv.fr
"""

import pandas as pd
import datetime
from functools import lru_cache

from pynsee.utils._request_insee import _request_insee

@lru_cache(maxsize=None)
def get_ascending_area(area: str, code: str, date: str = None, type: str = None):
    """
    Get information about areas containing a given area

    Args:
        area (str): case sensitive, area type, any of ('arrondissement', 'arrondissementMunicipal', 'circonscriptionTerritoriale', 'commune', 'communeAssociee', 'communeDeleguee', 'departement', 'district')
            
        code (str): area code

        type (str) : case insensitive, any of 'Arrondissement', 'Departement', 'Region', 'UniteUrbaine2020', 'ZoneDEmploi2020', ...

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default the current date is used.

    Examples:
        >>> from pynsee.localdata import get_ascending_area
        >>> df = get_ascending_area("commune", code='59350', date='2018-01-01')
        >>> df = get_ascending_area("departement", code='59')
    """

    areas = {
            'arrondissement', 
            'arrondissementMunicipal', 
            'circonscriptionTerritoriale', 
            'commune', 
            'communeAssociee', 
            'communeDeleguee', 
            'departement', 
            'district',
            }
    if area not in areas:
        msg = (
            f"territory must be one of {areas} "
            f"- found '{area}' instead"
            )
        raise ValueError(msg)
            
    
    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/V1/geo/"

    api_link = INSEE_localdata_api_link + area + "/" + str(code) + "/ascendants"

    if date is not None:
        api_link = api_link + "?date=" + date
    
    if type is not None:
        api_link += "&type=" + type

    request = _request_insee(api_url=api_link, file_format="application/json")

    try:
        data = request.json()

        list_data = []

        for i in range(len(data)):
            df = pd.DataFrame(data[i], index=[0])
            list_data.append(df)

        data_final = pd.concat(list_data).reset_index(drop=True)

    except:
        print("!!! No data found !!!")
        data_final = None

    return data_final