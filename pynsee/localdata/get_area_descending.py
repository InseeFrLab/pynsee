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
def _warning_territory_descendants():
    print("\ndate is None, by default it's supposed to be ten years before current year")


@lru_cache(maxsize=None)
def get_area_descending(area: str, code: str, date: str = None, type: str = None):
    """
    Get information about territories contained in a given territory

    Args:
        territory (str): case sensitive, territory type, any of ('aireDAttractionDesVilles2020', 'arrondissement', 'collectiviteDOutreMer', 'commune', 'departement', 'region', 'uniteUrbaine2020', 'zoneDEmploi2020')
            
        code (str): territory code

        type (str) : case insensitive, any of 'Arrondissement', 'Departement', 'Region', 'UniteUrbaine2020', 'ZoneDEmploi2020', ...

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default it supposed to be ten years before current year.

    Examples:
        >>> from pynsee.localdata import get_area_descending
        >>> df = get_area_descending("commune", code='59350', date='2018-01-01')
        >>> df = get_area_descending("departement", code='59', date='2018-01-01')
        >>> df = get_area_descending("zoneDEmploi2020", code='1109')
    """

    areas = {
            'aireDAttractionDesVilles2020', 
            'arrondissement', 
            'collectiviteDOutreMer', 
            'commune', 
            'departement', 
            'region', 
            'uniteUrbaine2020', 
            'zoneDEmploi2020',
            }
    if area not in areas:
        msg = (
            f"territory must be one of {areas} "
            f"- found '{area}' instead"
            )
        raise ValueError(msg)
            
    
    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/V1/geo/"

    api_link = INSEE_localdata_api_link + territory + "/" + str(code) + "/descendants"

    
    if date is not None:
        api_link = api_link + "?date=" + date
    #else:
        #_warning_territory_descendants()

        #now = datetime.datetime.now()
        #date = str(now.year - 10)
        #api_link = api_link + "?date=" + date + "-01-01"

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