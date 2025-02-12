import logging
import warnings

from functools import lru_cache
from typing import Union

import geopandas as gpd
import numpy as np
import pandas as pd

from tqdm.auto import tqdm
from shapely.errors import ShapelyDeprecationWarning

from pynsee.geodata import GeoFrDataFrame
from pynsee.utils.requests_session import PynseeAPISession
from pynsee.sirene._get_location_openstreetmap import (
    _get_location_openstreetmap,
)

logger = logging.getLogger(__name__)

tqdm.pandas(desc="Getting location")


@lru_cache(maxsize=None)
def _warning_get_location():
    logger.warning(
        "For at least one point, exact location has not been found, city "
        "location has been given instead"
    )


@lru_cache(maxsize=None)
def _warning_OSM():
    logger.info(
        "This function returns data made available by OpenStreetMap and its "
        "contributors.\n"
        "Please comply with Openstreetmap's Copyright and ODbL Licence"
    )


CONFIG_ADDRESSES = {
    "address": [
        "numeroVoieEtablissement",
        "typeVoieEtablissementLibelle",
        "libelleVoieEtablissement",
        "codePostalEtablissement",
        "libelleCommuneEtablissement",
    ],
    "address_backup": [
        "codePostalEtablissement",
        "libelleCommuneEtablissement",
    ],
}

NOMINATIM_RESULTS = ["latitude", "longitude", "category", "type", "importance"]


class SireneDataFrame(pd.DataFrame):
    """Class for handling dataframes built from INSEE SIRENE API's data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return SireneDataFrame

    def get_location(
        self, update=False
    ) -> Union[GeoFrDataFrame, "SireneDataFrame"]:
        """
        Get latitude and longitude from OpenStreetMap, add geometry column and
        turn ``SireneDataframe`` into ``GeoFrDataFrame``.

        Args:
            update (bool, optional): data is saved locally, set update=True to
                trigger an update. Defaults to False.

        Notes:
            If it fails to find the exact location, by default it returns the
            location of the city. Whether the exact location has been found or
            not is encoded in the `exact_location` column of the new
            ``GeoFrDataFrame``.

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
            warnings.filterwarnings(
                "ignore", category=ShapelyDeprecationWarning
            )

            df = self.reset_index(drop=True)

            list_col = [
                "siret",
                "numeroVoieEtablissement",
                "typeVoieEtablissementLibelle",
                "libelleVoieEtablissement",
                "codePostalEtablissement",
                "libelleCommuneEtablissement",
            ]

            if set(list_col).issubset(df.columns):

                addresses = df[CONFIG_ADDRESSES["address"]].fillna("")

                city = "libelleCommuneEtablissement"
                addresses[city] = addresses[city].str.replace(
                    "[0-9]|EME", "", case=False, regex=True
                )
                for field in [
                    city,
                    "libelleVoieEtablissement",
                    "typeVoieEtablissementLibelle",
                ]:
                    addresses[field] = addresses[field].str.replace(
                        r" (D|L) ", r" \1'", case=False, regex=True
                    )

                for field, config in CONFIG_ADDRESSES.items():
                    addresses[field] = (
                        pd.Series(addresses[config].values.tolist())
                        .str.join(" ")
                        .str.replace(" +", "+", regex=True)
                        .str.replace(" ", "+", regex=False)
                        .str.strip()
                    )
                    ix = addresses[addresses[field] != ""].index
                    addresses.loc[ix, field] += "+FRANCE"
                    ix = addresses[addresses[field] == ""].index
                    addresses.loc[ix, field] = np.nan

                with PynseeAPISession() as session:

                    def query_func(x):
                        try:
                            return _get_location_openstreetmap(
                                x,
                                session=session,
                                update=update,
                            )
                        except Exception:
                            return None

                    ix = addresses.index
                    for field in CONFIG_ADDRESSES:
                        sample = (
                            addresses.loc[ix, [field]]
                            .drop_duplicates()
                            .dropna()
                        )
                        sample["result"] = sample[field].progress_apply(
                            query_func
                        )
                        if "result" in addresses:
                            # simple hack to rename column for second config
                            sample = sample.rename(
                                {"result": "result2"}, axis=1
                            )
                            sample["exact_location"] = False
                        addresses = addresses.merge(
                            sample, on=field, how="left"
                        )
                        ix = addresses[addresses["result"].isnull()].index
                addresses["result"] = addresses["result"].combine_first(
                    addresses["result2"]
                )
                addresses = addresses.drop("result2", axis=1)
                addresses["exact_location"] = (
                    addresses["exact_location"].fillna(1).astype("bool")
                )

                def extract_data(tup):
                    try:
                        return dict(zip(NOMINATIM_RESULTS, tup))
                    except TypeError:
                        return {}

                results = pd.DataFrame(
                    addresses["result"].apply(extract_data).values.tolist()
                )
                addresses = addresses.drop("result", axis=1).join(results)

                addresses = addresses[["exact_location"] + NOMINATIM_RESULTS]
                addresses["geometry"] = gpd.points_from_xy(
                    x=addresses["longitude"], y=addresses["latitude"], crs=4326
                )
                addresses = addresses.drop(["latitude", "longitude"], axis=1)
                return GeoFrDataFrame(
                    self.join(addresses, how="left"), crs=4326
                )

            return df
