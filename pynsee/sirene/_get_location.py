# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import time
import re
import pandas as pd
from tqdm import trange
from datetime import datetime
from numpy import random
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from pynsee.sirene._get_location_openstreetmap import _get_location_openstreetmap

@lru_cache(maxsize=None)
def _warning_get_location():
    print("This function relies on OpenStreetMap (geopy package)\nPlease, change timeSleep argument if the maximum number of queries is reached\nIn the long run, this function may be depreciated")


def _get_location(df, timeSleep=1):
    """Get latitude and longitude of French legal entities

    Notes:
        This function uses OpenStreetMap through the geopy package.

        If it fails to find the exact location, by default it returns the location of the city.

    Args:
        df (DataFrame): It should be the output of the search_sirene function

    Examples:
        >>> from pynsee.metadata import get_activity_list
        >>> from pynsee.sirene import search_sirene, get_location
        >>> #
        >>> #  Get activity list
        >>> naf5 = get_activity_list('NAF5')
        >>> #
        >>> # Get alive legal entities belonging to the automotive industry
        >>> df = search_sirene(variable = ["activitePrincipaleEtablissement"],
        >>>                    pattern = ['29.10Z'], kind = 'siret')
        >>> #
        >>> # Keep businesses with more than 100 employees
        >>> df = df.loc[df['effectifsMinEtablissement'] > 100]
        >>> df = df.reset_index(drop=True)
        >>> #
        >>> # Get location
        >>> df_location = get_location(df)
    """

    _warning_get_location()

    def clean(string):
        if pd.isna(string):
            cleaned = ''
        else:
            cleaned = string
        return(cleaned)

    list_col = ['siret', 'numeroVoieEtablissement',
                'typeVoieEtablissementLibelle', 'libelleVoieEtablissement',
                'codePostalEtablissement', 'libelleCommuneEtablissement']

    if set(list_col).issubset(df.columns):

        list_location = []

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=timeSleep)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        for i in trange(len(df.index), desc='Getting location'):

            siret = clean(df.loc[i, 'siret'])
            nb = clean(df.loc[i, 'numeroVoieEtablissement'])
            street_type = clean(df.loc[i, 'typeVoieEtablissementLibelle'])
            street_name = clean(df.loc[i, 'libelleVoieEtablissement'])

            postal_code = clean(df.loc[i, 'codePostalEtablissement'])
            city = clean(df.loc[i, 'libelleCommuneEtablissement'])
            city = re.sub('[0-9]|EME', '', city)

            address = '{}+{}+{}+{}+{}+FRANCE'.format(
                nb, street_type, street_name, postal_code, city)
            address = re.sub(' L ', " L'", address)
            address = re.sub(' D ', " D'", address)
           
            try:
                lat, lon, category, typeLoc = _get_location_openstreetmap(query=address, session=session)
            except:
                address = '{}+{}+FRANCE'.format(postal_code, city)
                try:
                    lat, lon, category, typeLoc = _get_location_openstreetmap(query=address, session=session)
                except:
                    lat, lon, category, typeLoc = (None, None, None, None)
                
            df_location = pd.DataFrame({'siret': siret,
                                        'latitude': lat,
                                        'longitude': lon,
                                        'category': category,
                                        'type': typeLoc}, index=[0])

            list_location.append(df_location)

        df_location = pd.concat(list_location)
        df_location = df_location.reset_index(drop=True)

        return(df_location)
