
import time
import re
import pandas as pd
from tqdm import trange
from datetime import datetime
from numpy import random
import numpy as np
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString, MultiPoint

from pynsee.geodata.GeoDataframe import GeoDataframe
from pynsee.sirene._get_location_openstreetmap import _get_location_openstreetmap

@lru_cache(maxsize=None)
def _warning_get_location():
    print("!!!\nThis function relies on OpenStreetMap\nPlease, change timeSleep argument if the maximum number of queries is reached\nBeware, maintenance of this function should not be taken for granted!\n!!!")

class SireneDataframe(pd.DataFrame):
    """Class for handling dataframes built from INSEE SIRENE API's data

    """  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return SireneDataframe
    
    def get_location(self):
        """Get latitude and longitude from OpenStreetMap, add geometry column and turn SireneDataframe into GeoDataframe

        Notes:
            This function uses OpenStreetMap through the geopy package.

            If it fails to find the exact location, by default it returns the location of the city.

        Args:
            df (SireneDataframe): It should be a SireneDataframe from search_data or get_data

        Examples:
            >>> from pynsee.metadata import get_activity_list
            >>> from pynsee.sirene import search_sirene
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
            >>> df = df.get_location()
        """

        df = self

        # _warning_get_location()

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
            timeSleep = 1
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

                city = re.sub(' D ', " D'", re.sub(' L ', " L'", city))
                street_name = re.sub(' D ', " D'", re.sub(' L ', " L'", street_name))
                street_type = re.sub(' D ', " D'", re.sub(' L ', " L'", street_type))

                list_var = []
                for var in [nb, street_type, street_name, postal_code, city]:
                    if var != "":
                        list_var += [re.sub(' ', '+', var)]
                
                query = "+".join(list_var)
                if query != "":
                    query += '+FRANCE'

                list_var_backup = []
                for var in [postal_code, city]:
                    if var != "":
                        list_var_backup += [re.sub(' ', '+', var)]
                
                query_backup = "+".join(list_var)
                if query_backup != "":
                    query_backup += '+FRANCE'
                            
                try:
                    lat, lon, category, typeLoc, importance = _get_location_openstreetmap(query=query, session=session)
                except:                
                    try:
                        lat, lon, category, typeLoc, importance = _get_location_openstreetmap(query=query_backup, session=session)
                        importance = None
                    except:
                        lat, lon, category, typeLoc, importance = (None, None, None, None, None)
                    
                df_location = pd.DataFrame({'siret': siret,
                                            'latitude': lat,
                                            'longitude': lon,
                                            'category': category,
                                            'type': typeLoc,
                                            'importance' : importance}, index=[0])

                list_location.append(df_location)

            df_location = pd.concat(list_location)
            df_location = df_location.reset_index(drop=True)

            sirene_df = pd.merge(self, df_location, on = 'siret', how = 'left')
            
            sirene_df['latitude'] = pd.to_numeric(sirene_df['latitude'])
            sirene_df['longitude'] = pd.to_numeric(sirene_df['longitude'])
            list_points = []

            for i in range(len(sirene_df.index)):

                if (sirene_df.loc[i,'latitude'] is None) or np.isnan(sirene_df.loc[i,'latitude']):                
                    list_points += [None]
                else:
                    list_points += [Point(sirene_df.loc[i,'longitude'], sirene_df.loc[i,'latitude'])]
           
            sirene_df['geometry'] = list_points

            GeoDF = GeoDataframe(sirene_df)

            return(GeoDF)
