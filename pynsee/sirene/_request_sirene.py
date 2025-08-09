# Copyright : INSEE, 2021

import pandas as pd
import math
from functools import lru_cache

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.sirene._make_dataframe import _make_dataframe

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _request_sirene(query, kind, number=1001):

    if kind == "siren":
        main_key = "unitesLegales"
    elif kind == "siret":
        main_key = "etablissements"
    else:
        raise ValueError("!!! kind should be among : siren siret !!!")

    INSEE_api_sirene_siren = "https://api.insee.fr/api-sirene/3.11"
    number_query_limit = 1000

    number_query = min(number_query_limit, number)

    n_query_total = math.ceil(number / number_query_limit)
    i_query = 1
    query_number = "{}/{}".format(i_query, n_query_total)

    main_query = INSEE_api_sirene_siren + "/" + kind + query

    link = main_query + "&nombre={}".format(number_query)

    if number > number_query_limit:
        link = link + "&curseur=*"

    with PynseeAPISession() as session:
        request = session.request_insee(
            api_url=link,
            file_format="application/json;charset=utf-8",
        )

    list_dataframe = []

    request_status = request.status_code

    if request_status == 200:
        data_request = request.json()

        data_request_1 = _make_dataframe(data_request, main_key, "1")

        if "siret" in data_request_1.columns:
            df_nrows = len(data_request_1.siret.unique())
        elif "siren" in data_request_1.columns:
            df_nrows = len(data_request_1.siren.unique())
        else:
            df_nrows = len(data_request_1.index.unique())

        list_dataframe.append(data_request_1)

        list_header_keys = list(data_request["header"].keys())

        if "curseur" in list_header_keys:
            cursor = data_request["header"]["curseur"]
            following_cursor = data_request["header"]["curseurSuivant"]

            #  & (i_query < query_limit)
            while (
                (following_cursor != cursor)
                & (request_status == 200)
                & (df_nrows < number)
            ):
                i_query += 1
                query_number = "{}/{}".format(i_query, n_query_total)

                new_query = (
                    main_query
                    + "&nombre={}".format(number_query_limit)
                    + "&curseur="
                    + following_cursor
                )

                with PynseeAPISession() as session:
                    request_new = session.request_insee(
                        api_url=new_query,
                        file_format="application/json;charset=utf-8",
                    )

                request_status = request_new.status_code

                if request_status == 200:
                    data_request_new = request_new.json()
                    cursor = data_request_new["header"]["curseur"]
                    following_cursor = data_request_new["header"][
                        "curseurSuivant"
                    ]

                    if len(data_request_new[main_key]) > 0:
                        df = _make_dataframe(
                            data_request_new, main_key, query_number
                        )

                        if "siret" in df.columns:
                            df_nrows += len(df.siret.unique())
                        elif "siren" in df.columns:
                            df_nrows += len(df.siren.unique())
                        else:
                            df_nrows += len(df.index.unique())

                        list_dataframe.append(df)
                    else:
                        logger.debug(
                            "{} - No more data found".format(query_number)
                        )

                    if cursor == following_cursor:
                        i_query += 1
                        query_number = "{}/{}".format(i_query, n_query_total)
                        logger.debug(
                            "{} - No more data found".format(query_number)
                        )

                    if df_nrows == number:
                        logger.warning(
                            "maximum reached, "
                            "increase value of number argument !"
                        )

        data_final = pd.concat(list_dataframe)

        if "siret" in data_final.columns:
            sirenCol = "siret"
        elif "siren" in data_final.columns:
            sirenCol = "siren"
        else:
            sirenCol = None

        if sirenCol is not None:
            if len(data_final[sirenCol].unique()) == number_query_limit:
                logger.warning(
                    "The query reached maximum item limit, "
                    "please change argument number to get more than "
                    f"{number_query_limit} different {sirenCol}"
                )

        return data_final
    else:
        logger.error(request.text)
        return None
