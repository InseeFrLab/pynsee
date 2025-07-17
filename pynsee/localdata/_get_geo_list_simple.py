# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession


@lru_cache(maxsize=None)
def _get_geo_list_simple(geo, date=None, progress_bar=False):
    api_url = "https://api.insee.fr/metadonnees/geo/" + geo
    if date:
        api_url += f"?date={date}"

    with PynseeAPISession() as session:
        results = session.request_insee(
            api_url=api_url, file_format="application/json"
        )

    df_geo = pd.DataFrame(results.json())

    df_geo = df_geo.rename(
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

    return df_geo
