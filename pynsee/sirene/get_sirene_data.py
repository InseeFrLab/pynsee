# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from functools import lru_cache
import sys
import os
import re

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict
from pynsee.sirene.SireneDataFrame import SireneDataFrame


@lru_cache(maxsize=None)
def _warning_get_data():
    print(
        "\n!!! This function may return personal data, please check and\n comply with the legal framework relating to personal data protection !!!"
    )


def get_sirene_data(*id):
    """Get data about one or several companies from siren or siret identifiers

    Notes:
        This function may return personal data, please check and comply with the legal framework relating to personal data protection

    Examples:
        >>> from pynsee.sirene import get_sirene_data
        >>> df = get_sirene_data("552081317", "32227167700021")
        >>> df = get_sirene_data(['32227167700021', '26930124800077'])
    """

    list_ids = []

    for i in range(len(id)):
        if isinstance(id[i], list):
            list_ids += id[i]
        elif isinstance(id[i], pd.core.series.Series):
            list_ids += id[i].to_list()
        elif isinstance(id[i], str):
            list_ids += [id[i]]
        else:
            list_ids += [str(id[i])]

    list_data = []

    for i in range(len(list_ids)):

        for kind in ["siret", "siren"]:

            if kind == "siren":
                main_key = "uniteLegale"
            elif kind == "siret":
                main_key = "etablissement"

            INSEE_api_sirene = "https://api.insee.fr/entreprises/sirene/V3/" + kind
            link = INSEE_api_sirene + "/" + re.sub(r"\s+", "", str(list_ids[i]))

            try:
                sys.stdout = open(os.devnull, "w")
                request = _request_insee(
                    api_url=link, file_format="application/json;charset=utf-8"
                )

                data_request = request.json()
                sys.stdout = sys.__stdout__

                try:
                    data = data_request[main_key]
                except:
                    main_key_list = [
                        key for key in list(data_request.keys()) if key != "header"
                    ]
                    main_key = main_key_list[0]
                    data = data_request[main_key]

                data_final = _make_dataframe_from_dict(data)
            except:
                pass
            else:
                list_data.append(data_final)
                break

    if len(list_data) > 0:
        data_final = pd.concat(list_data).reset_index(drop=True)
    else:
        raise ValueError("!!! No data found for the provided identifiers !!!")

    _warning_get_data()

    SireneDF = SireneDataFrame(data_final)

    return SireneDF
