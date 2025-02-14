# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
import datetime
from functools import lru_cache

from pynsee.utils.requests_session import PynseeAPISession

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_get_new_city():
    logger.info(
        "date is None, by default it is supposed to be ten years before "
        "current year"
    )


@lru_cache(maxsize=None)
def get_new_city(code, date=None):
    """Get data about the new city made from the old ones

    Notes:
        Local data is always provided with a cities classification which depends on a year.
        This classification evolves over time due to the merger of some cities.
        It is often useful to keep track of these mergers to reconcile some data.

        To get a city at a given date, use get_area_projection instead.

    Args:
        code (str): city code

        date (str, optional): date used to analyse the data, format : 'AAAA-MM-JJ'. If date is None, by default it supposed to be ten years before current year.

    Examples:
        >>> from pynsee.localdata import get_next_city
        >>> df = get_next_city(code = '24431', date = '2018-01-01')
    """
    INSEE_localdata_api_link = "https://api.insee.fr/metadonnees/geo/"

    api_link = INSEE_localdata_api_link + "commune/" + str(code) + "/suivants"

    if date is not None:
        api_link = api_link + "?date=" + date
    else:
        _warning_get_new_city()

        now = datetime.datetime.now()
        date = str(now.year - 10)
        api_link = api_link + "?date=" + date + "-01-01"

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
