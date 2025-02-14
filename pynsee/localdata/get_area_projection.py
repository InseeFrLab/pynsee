# -*- coding: utf-8 -*-

import pandas as pd
import datetime
from functools import lru_cache

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_get_area_projection():
    logger.info(
        "dateProjection is None, by default it is supposed to be the current "
        "date"
    )


@save_df(day_lapse_max=90)
def get_area_projection(
    area: str,
    code: str,
    date: str,
    dateProjection: str = None,
    silent: bool = False,
):
    """
    Get data about the area (valid at given `date` datetime) projected
    at `dateProjection` datetime.

    Args:
        area (str): case insensitive, area type, any of (
            'arrondissement',
            'arrondissementMunicipal',
            'commune',
            'departement',
            'region'
            )

        code (str): city code

        date (str): date used to analyse the data, format : 'AAAA-MM-JJ'.

        dateProjection (str, optional): date used to project the area into,
            format : 'AAAA-MM-JJ'.  If dateProjection is None, by default it
            is supposed to be the current date (ie projection into today's
            value)

        silent (bool, optional): Set to True, to disable messages printed in log info

    Examples:
        >>> from pynsee.localdata import get_area_projection
        >>> df = get_area_projection(
                code='01039',
                date='2020-01-01',
                dateProjection='2023-04-01'
                )
    """

    areas = {
        "arrondissement": "arrondissement",
        "arrondissementmunicipal": "arrondissementMunicipal",
        "commune": "commune",
        "departement": "departement",
        "intercommunalite": "intercommunalite",
        "region": "region",
    }
    if area.lower() not in areas:
        msg = f"territory must be one of {areas} - found '{area}' instead"
        raise ValueError(msg)
    else:
        area = areas[area.lower()]

    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/geo/"

    api_link = f"{INSEE_localdata_api_link}{area}/{code}/projetes?date={date}"

    if not dateProjection:
        _warning_get_area_projection()
        dateProjection = datetime.date.today().strftime("%Y-%m-%d")

    api_link += f"&dateProjection={dateProjection}"

    try:
        with PynseeAPISession() as session:
            request = session.request_insee(
                api_url=api_link, file_format="application/json"
            )

        data = pd.DataFrame(request.json())

    except Exception:
        logger.error(
            f"No data found for projection of area {area} of code {code} "
            f"from date {date} to date {dateProjection}"
        )
        data = pd.DataFrame()

    return data
