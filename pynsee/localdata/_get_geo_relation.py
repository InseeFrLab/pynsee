# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

from pynsee.utils._paste import _paste
from pynsee.utils.requests_session import PynseeAPISession


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

    with PynseeAPISession() as session:
        results = session.request_insee(
            api_url=api_url, file_format="application/json"
        )

    df_relation_all = pd.DataFrame(results.json())
    df_relation_all = df_relation_all.assign(geo_init=code)
    df_relation_all = df_relation_all.rename(
        {
            "code": "CODE",
            "uri": "URI",
            "chefLieu": "CHEFLIEU",
            "type": "TYPE",
            "intitule": "TITLE",
            "dateCreation": "DATECREATION",
            "dateSuppression": "DATESUPPRESSION",
            "intituleSansArticle": "TITLE_SHORT",
        },
        axis=1,
    ).drop("typeArticle", axis=1)

    return df_relation_all
