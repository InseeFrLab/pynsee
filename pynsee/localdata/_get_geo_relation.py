# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import io
import pandas as pd
import xml.etree.ElementTree as ET

from pynsee.utils._paste import _paste
from pynsee.utils._request_insee import _request_insee


@lru_cache(maxsize=None)
def _get_geo_relation(geo, code, relation, date=None, type=None):

    # relation_list = ['ascendants', 'descendants', 'suivants', 'precedents', 'projetes']
    # list_available_geo = ['communes', 'regions', 'departements',
    #                       'arrondissements', 'arrondissementsMunicipaux']
    # code = '11'
    # geo = 'region'
    # relation = 'descendants'

    # idf = _get_geo_relation('region', "11", 'descendants')
    # essonne = _get_geo_relation('region', "11", 'ascendants')

    # api_url = (
    #     "https://api.insee.fr/metadonnees/V1/geo/"
    #     + geo
    #     + "/"
    #     + code
    #     + "/"
    #     + relation
    # )
    api_url = (
        "https://api.insee.fr/metadonnees/geo/"
        + geo
        + "/"
        + code
        + "/"
        + relation
    )

    parameters = ["date", "type"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))

    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse="&")
        api_url = api_url + added_param_string

    results = _request_insee(api_url=api_url)

    raw_data_file = io.BytesIO(results.content)

    root = ET.parse(raw_data_file).getroot()

    n_geo = len(root)

    list_geo_relation = []

    for igeo in range(n_geo):
        n_var = len(root[igeo])

        dict_var = {}

        for ivar in range(n_var):
            dict_var[root[igeo][ivar].tag] = root[igeo][ivar].text

        dict_var = {**dict_var, **root[igeo].attrib}
        df_relation = pd.DataFrame(dict_var, index=[0])
        list_geo_relation.append(df_relation)

    df_relation_all = pd.concat(list_geo_relation)
    df_relation_all = df_relation_all.assign(geo_init=code)

    return df_relation_all
