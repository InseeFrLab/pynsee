# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:52:54 2023

@author: thomas.grandjean@developpement-durable.gouv.fr
"""

import pandas as pd
from functools import lru_cache
import os

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_ascending_area(
    area: str,
    code: str,
    date: str = None,
    type: str = None,
    update: bool = False,
):
    """
    Get information about areas containing a given area

    Args:
        area (str): case sensitive, area type, any of ('arrondissement', 'arrondissementMunicipal', 'circonscriptionTerritoriale', 'commune', 'communeAssociee', 'communeDeleguee', 'departement', 'district')

        code (str): area code

        type (str) : case insensitive, any of 'Arrondissement', 'Departement', 'Region', 'UniteUrbaine2020', 'ZoneDEmploi2020', ...

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default the current date is used.

        update (bool): locally saved data is used by default. Trigger an update with update=True.

    Examples:
        >>> from pynsee.localdata import get_ascending_area
        >>> df = get_ascending_area("commune", code='59350', date='2018-01-01')
        >>> df = get_ascending_area("departement", code='59')
    """

    areas = {
        "arrondissement",
        "arrondissementMunicipal",
        "circonscriptionTerritoriale",
        "commune",
        "communeAssociee",
        "communeDeleguee",
        "departement",
        "district",
    }
    if area not in areas:
        msg = f"area must be one of {areas} " f"- found '{area}' instead"
        raise ValueError(msg)

    params_hash = ["get_ascending_area", area, code, date, type]
    params_hash = [x if x else "_" for x in params_hash]
    filename = _hash("".join(params_hash))
    insee_folder = _create_insee_folder()
    file_data = insee_folder + "/" + filename

    if (not os.path.exists(file_data)) or update:
        INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/V1/geo/"

        api_link = INSEE_localdata_api_link + area + f"/{code}/ascendants?"

        params = []
        if date is not None:
            params.append(f"date={date}")
        if type is not None:
            params.append(f"type={type}")

        api_link = api_link + "&".join(params)

        request = _request_insee(
            api_url=api_link, file_format="application/json"
        )

        try:
            data = request.json()
            list_data = []

            for i in range(len(data)):
                df = pd.DataFrame(data[i], index=[0])
                list_data.append(df)

            data_final = pd.concat(list_data).reset_index(drop=True)

            data_final.to_pickle(file_data)
            print(f"Data saved: {file_data}")

        except Exception:
            logger.error("No data found !")
            data_final = None

    else:
        try:
            data_final = pd.read_pickle(file_data)
        except Exception:
            os.remove(file_data)
            data_final = get_ascending_area(
                area=area, code=code, date=date, type=type, update=True
            )
        else:
            logger.info(
                "Locally saved data has been used\n"
                "Set update=True to trigger an update"
            )

    return data_final
