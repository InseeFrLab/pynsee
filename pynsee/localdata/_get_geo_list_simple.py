# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
from functools import lru_cache
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import trange

from pynsee.utils.requests_session import PynseeAPISession


@lru_cache(maxsize=None)
def _get_geo_list_simple(geo, date=None, progress_bar=False):
    api_url = "https://api.insee.fr/metadonnees/geo/" + geo
    if date:
        api_url += f"?date={date}"

    with PynseeAPISession() as session:
        results = session.request_insee(api_url=api_url)

    raw_data_file = io.BytesIO(results.content)

    root = ET.parse(raw_data_file).getroot()

    n_variable = len(root)

    list_data_geo = []

    if progress_bar is True:
        geo_range = trange(n_variable, desc="Getting %s" % geo, leave=False)
    else:
        geo_range = range(n_variable)

    for igeo in geo_range:
        n_var = len(root[igeo])

        dict_geo = {}

        for ivar in range(n_var):
            dict_geo[root[igeo][ivar].tag] = root[igeo][ivar].text

        dict_geo = {**dict_geo, **root[igeo].attrib}

        data_geo = pd.DataFrame(dict_geo, index=[0])

        list_data_geo.append(data_geo)

    df_geo = pd.concat(list_data_geo, ignore_index=True)
    return df_geo
