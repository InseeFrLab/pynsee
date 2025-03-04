# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
from functools import lru_cache
import pandas as pd
import xml.dom.minidom
from tqdm import trange

from pynsee.macrodata._get_date import _get_date
from pynsee.utils.requests_session import PynseeAPISession

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_insee(api_query, sdmx_query, step="1/1"):

    with PynseeAPISession() as session:
        results = session.request_insee(sdmx_url=sdmx_query, api_url=api_query)

    raw_data_file = io.BytesIO(results.content)

    # parse the xml file
    root = xml.dom.minidom.parse(raw_data_file)

    n_series = len(root.getElementsByTagName("Series"))

    #
    # for all series, observations and attributes (depending on time)
    # collect the data (3 loops)
    #

    list_series = []

    for j in trange(n_series, desc="%s - Getting series" % step):
        data = root.getElementsByTagName("Series")[j]

        n_obs = len(data.getElementsByTagName("Obs"))

        #
        # collect the obsevation values from the series
        #

        list_obs = []

        for i in range(n_obs):
            obs = data.getElementsByTagName("Obs")[i]._attrs

            dict_obs = {}
            for a in obs:
                dict_obs[a] = obs[a]._value

            col = list(dict_obs.keys())

            df = pd.DataFrame(dict_obs, columns=col, index=[0])

            list_obs.append(df)

        if len(list_obs) > 0:
            obs_series = pd.concat(list_obs).reset_index(drop=True)

        #
        # collect attributes values from the series
        #

        attr_series = data._attrs

        dict_attr = {}
        for a in attr_series:
            dict_attr[a] = attr_series[a]._value

        col_attr = list(dict_attr.keys())
        attr_series = pd.DataFrame(
            dict_attr, columns=col_attr, index=[0]
        ).reset_index(drop=True)

        if len(list_obs) > 0:
            data_series = obs_series
            if len(dict_attr.keys()) > 0:
                for k in dict_attr.keys():
                    data_series[k] = dict_attr[k]
            # data_series = pd.concat([obs_series, attr_series], axis=1)
        else:
            data_series = pd.concat([attr_series], axis=1)

        #
        # add date column
        #

        if len(list_obs) > 0:
            freq = attr_series.FREQ[0]
            time_period = obs_series.TIME_PERIOD.to_list()

            dates = _get_date(freq, time_period)
            # new column
            data_series = data_series.assign(DATE=dates)
            # place DATE column in the first position
            data_series = data_series[
                ["DATE"] + [c for c in data_series if c not in ["DATE"]]
            ]

        # append series dataframe to final list
        list_series.append(data_series)

    data_final = pd.concat(list_series)

    # index and sort dataframe by date
    # data_final = data_final.set_index('DATE')
    if "DATE" in data_final.columns:
        data_final = data_final.sort_values(["IDBANK", "DATE"])

    # harmonise column names
    colnames = data_final.columns

    def replace_hyphen(x):
        return str(x).replace("-", "_")

    newcolnames = list(map(replace_hyphen, colnames))
    data_final.columns = newcolnames

    if "OBS_VALUE" in data_final.columns:
        data_final["OBS_VALUE"] = data_final["OBS_VALUE"].apply(
            pd.to_numeric, errors="coerce"
        )

    logger.debug("Data has been cached")

    return data_final
