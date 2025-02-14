# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:52:54 2023

@author: thomas.grandjean@developpement-durable.gouv.fr
"""

import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df

import logging

logger = logging.getLogger(__name__)


@save_df(day_lapse_max=90)
def get_ascending_area(
    area: str,
    code: str,
    date: str = None,
    type: str = None,
    update: bool = False,
    silent: bool = False,
):
    """
    Get information about areas containing a given area

    Args:
        area (str): case sensitive, area type, any of ('arrondissement', 'arrondissementMunicipal', 'circonscriptionTerritoriale', 'commune', 'communeAssociee', 'communeDeleguee', 'departement', 'district')

        code (str): area code

        type (str) : case insensitive, any of 'Arrondissement', 'Departement', 'Region', 'UniteUrbaine2020', 'ZoneDEmploi2020', ...

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default the current date is used.

        update (bool): locally saved data is used by default. Trigger an update with update=True.

        silent (bool, optional): Set to True to disable messages printed in log info

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

    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/geo/"

    api_link = INSEE_localdata_api_link + area + f"/{code}/ascendants?"

    params = []
    if date is not None:
        params.append(f"date={date}")
    if type is not None:
        params.append(f"type={type}")

    api_link = api_link + "&".join(params)

    with PynseeAPISession() as session:
        request = session.request_insee(
            api_url=api_link, file_format="application/json"
        )

    try:
        data = request.json()

        list_data = []

        for i in range(len(data)):
            df = pd.DataFrame(data[i], index=[0])
            list_data.append(df)

        data_final = pd.concat(list_data).reset_index(drop=True)

    except Exception:
        logger.error("No data found !")
        data_final = pd.DataFrame()

    return data_final
