# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from functools import lru_cache

from pynsee.utils.requests_session import PynseeAPISession
import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_old_city(code, date=None):
    """Get data about the old cities made from the new one

    Notes:
        Local data is always provided with a cities classification which depends on a year.
        This classification evolves over time due to the merger of some cities.
        It is often useful to keep track of these mergers to reconcile some data.

    Args:
        code (str): city code

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default it supposed to be the current year.

    Examples:
        >>> from pynsee.localdata import get_old_city
        >>> df = get_old_city(code = '24259')
    """
    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/geo/"

    api_link = (
        INSEE_localdata_api_link + "commune/" + str(code) + "/precedents"
    )

    if date is not None:
        api_link = api_link + "?date=" + date

    with PynseeAPISession() as session:
        request = session.request_insee(
            api_url=api_link, file_format="application/json"
        )

    try:
        data = request.json()
        data_final = pd.DataFrame(data)

    except Exception:
        logger.error("No data found !")
        data_final = pd.DataFrame()

    return data_final
