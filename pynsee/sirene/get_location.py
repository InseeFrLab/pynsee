import re
import pandas as pd
from tqdm import trange
import numpy as np
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from shapely.geometry import Point
import warnings
from shapely.errors import ShapelyDeprecationWarning

from pynsee.geodata.GeoFrDataFrame import GeoFrDataFrame
from pynsee.sirene._get_location_openstreetmap import _get_location_openstreetmap


@lru_cache(maxsize=None)
def _warning_get_location():
    print(
        "For at least one point, exact location has not been found, city location has been given instead"
    )

@lru_cache(maxsize=None)
def _warning_OSM():
    print("This function returns data made available by OpenStreetMap and its contributors")
    print("Please comply with Openstreetmap's Copyright and ODbL Licence")

def get_location(self):
    """Get latitude and longitude from OpenStreetMap, add geometry column and turn SireneDataframe into GeoFrDataFrame

    Notes:
        If it fails to find the exact location, by default it returns the location of the city.

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
    _warning_OSM()    
    
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

        df = self.reset_index(drop=True)

        def clean(string):
            if pd.isna(string):
                cleaned = ""
            else:
                cleaned = string
            return cleaned

        list_col = [
            "siret",
            "numeroVoieEtablissement",
            "typeVoieEtablissementLibelle",
            "libelleVoieEtablissement",
            "codePostalEtablissement",
            "libelleCommuneEtablissement",
        ]

        if set(list_col).issubset(df.columns):

            list_location = []
            timeSleep = 1
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=timeSleep)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            for i in trange(len(df.index), desc="Getting location"):

                siret = clean(df.loc[i, "siret"])
                nb = clean(df.loc[i, "numeroVoieEtablissement"])
                street_type = clean(df.loc[i, "typeVoieEtablissementLibelle"])
                street_name = clean(df.loc[i, "libelleVoieEtablissement"])

                postal_code = clean(df.loc[i, "codePostalEtablissement"])
                city = clean(df.loc[i, "libelleCommuneEtablissement"])
                city = re.sub("[0-9]|EME", "", city)

                city = re.sub(" D ", " D'", re.sub(" L ", " L'", city))
                street_name = re.sub(" D ", " D'", re.sub(" L ", " L'", street_name))
                street_type = re.sub(" D ", " D'", re.sub(" L ", " L'", street_type))

                list_var = []
                for var in [nb, street_type, street_name, postal_code, city]:
                    if var != "":
                        list_var += [re.sub(" ", "+", var)]

                query = "+".join(list_var)
                if query != "":
                    query += "+FRANCE"

                list_var_backup = []
                for var in [postal_code, city]:
                    if var != "":
                        list_var_backup += [re.sub(" ", "+", var)]

                query_backup = "+".join(list_var_backup)
                if query_backup != "":
                    query_backup += "+FRANCE"

                try:
                    (
                        lat,
                        lon,
                        category,
                        typeLoc,
                        importance,
                    ) = _get_location_openstreetmap(query=query, session=session)
                except:
                    try:
                        (
                            lat,
                            lon,
                            category,
                            typeLoc,
                            importance,
                        ) = _get_location_openstreetmap(
                            query=query_backup, session=session
                        )
                        importance = None
                    except:
                        lat, lon, category, typeLoc, importance = (
                            None,
                            None,
                            None,
                            None,
                            None,
                        )
                    else:
                        _warning_get_location()

                df_location = pd.DataFrame(
                    {
                        "siret": siret,
                        "latitude": lat,
                        "longitude": lon,
                        "category": category,
                        "crs": "EPSG:4326",
                        "type": typeLoc,
                        "importance": importance,
                    },
                    index=[0],
                )

                list_location.append(df_location)

            df_location = pd.concat(list_location)
            df_location = df_location.reset_index(drop=True)

            sirene_df = pd.merge(self, df_location, on="siret", how="left")

            sirene_df["latitude"] = pd.to_numeric(sirene_df["latitude"])
            sirene_df["longitude"] = pd.to_numeric(sirene_df["longitude"])
            list_points = []

            for i in range(len(sirene_df.index)):

                if (sirene_df.loc[i, "latitude"] is None) or np.isnan(
                    sirene_df.loc[i, "latitude"]
                ):
                    list_points += [None]
                else:
                    list_points += [
                        Point(
                            sirene_df.loc[i, "longitude"], sirene_df.loc[i, "latitude"]
                        )
                    ]

            sirene_df["geometry"] = list_points

            GeoDF = GeoFrDataFrame(sirene_df)

            return GeoDF
        else:
            return df
