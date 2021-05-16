# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import re
import pandas as pd
from tqdm import trange
from datetime import datetime
from numpy import random
from pynsee.utils._hash import _hash

def get_location(df):    
    """Get latitude and longitude of French legal entities

    Notes:
        This function uses OpenStreetMap through the geopy package.

        If it fails to find the exact location, by default it returns the location of the city.

    Args:
        df (DataFrame): It should be the output of the search_sirene function

    Examples: 
        >>> from pynsee.metadata import get_activity_list
        >>> from pynsee.sirene import *
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
    from geopy.geocoders import Nominatim
    
    def clean(string):
        if pd.isna(string):
            cleaned = ''
        else:
            cleaned = string
        return(cleaned)
    
    list_col = ['siret', 'numeroVoieEtablissement',
                'typeVoieEtablissementLibelle', 'libelleVoieEtablissement',
                'codePostalEtablissement', 'libelleCommuneEtablissement']
         
    geolocator = Nominatim(user_agent = _hash(str(random.randint(1000)) + str(datetime.now())))
    #geolocator = Nominatim(user_agent = 'pynsee_python_package')

    if set(list_col).issubset(df.columns):    
    
        list_location = []
        
        for i in trange(len(df.index), desc = 'Getting location'):
        
            siret = clean(df.loc[i, 'siret'])
            nb = clean(df.loc[i, 'numeroVoieEtablissement'])
            street_type = clean(df.loc[i, 'typeVoieEtablissementLibelle'])
            street_name = clean(df.loc[i, 'libelleVoieEtablissement'])
        
            postal_code = clean(df.loc[i, 'codePostalEtablissement'])
            city = clean(df.loc[i, 'libelleCommuneEtablissement'])
            city = re.sub('[0-9]|EME', '', city)
        
            address = '{} {} {} {} {} FRANCE'.format(nb, street_type, street_name, postal_code, city)
            address = re.sub(' L ', " L'", address)
            address = re.sub(' D ', " D'", address)
            
            location = geolocator.geocode(address)
            
            try:
                lat = location.latitude
                long = location.longitude
                precision = 'exact'
            except:
                address = '{} {} FRANCE'.format(postal_code, city)           
            
                location = geolocator.geocode(address)
                
                try:
                    lat = location.latitude
                    long = location.longitude
                    precision = 'city'
                except:
                    lat = None
                    long = None
                    precision = None
                
            df_location = pd.DataFrame({'siret' : siret,   
                                        'latitude' : lat,
                                        'longitude' : long,
                                        'precision' : precision}, index=[0])

            list_location.append(df_location)    
            
        df_location = pd.concat(list_location)
        df_location = df_location.reset_index(drop=True)
        
        return(df_location)
    