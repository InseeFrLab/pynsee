# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import trange
import os

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._get_temp_dir import _get_temp_dir


@lru_cache(maxsize=None)
def _get_geo_list_simple(geo, progress_bar=False):

    api_url = "https://api.insee.fr/metadonnees/V1/geo/" + geo
    results = _request_insee(api_url=api_url, sdmx_url=None)

    dirpath = _get_temp_dir()

    raw_data_file = dirpath + "\\" + "raw_data_file"

    with open(raw_data_file, "wb") as f:
        f.write(results.content)

    root = ET.parse(raw_data_file).getroot()

    if os.path.exists(raw_data_file):
        os.remove(raw_data_file)

    n_variable = len(root)

    list_data_geo = []

    if progress_bar is True:
        geo_range = trange(n_variable, desc="Getting %s" % geo)
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

    df_geo = pd.concat(list_data_geo)
    return df_geo
