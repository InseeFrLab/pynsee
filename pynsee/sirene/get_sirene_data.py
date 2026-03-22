# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import logging
import re
from functools import lru_cache

import pandas as pd
from requests import RequestException

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict
from pynsee.utils.HiddenPrints import HiddenPrints

from .sirenedataframe import SireneDataFrame


logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_get_data():
    logger.warning(
        "This function may return personal data, please check and comply "
        "with the legal framework relating to personal data protection !"
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

    for sid in list_ids:
        for kind in ["siret", "siren"]:
            if kind == "siren":
                main_key = "uniteLegale"
            elif kind == "siret":
                main_key = "etablissement"

            INSEE_api_sirene = "https://api.insee.fr/api-sirene/3.11/" + kind
            link = INSEE_api_sirene + "/" + re.sub(r"\s+", "", str(sid))

            try:
                with HiddenPrints():
                    with PynseeAPISession() as session:
                        request = session.request_insee(
                            api_url=link,
                            file_format="application/json;charset=utf-8",
                            raise_if_not_ok=True,
                        )

                    data_request = request.json()
                try:
                    data = data_request[main_key]
                except Exception:
                    main_key_list = [
                        key
                        for key in list(data_request.keys())
                        if key != "header"
                    ]
                    main_key = main_key_list[0]
                    data = data_request[main_key]

                data_final = _make_dataframe_from_dict(data)
            except RequestException as e:
                if e.response.status_code == 401:
                    raise
            except Exception:
                pass
            else:
                list_data.append(data_final)
                break

    if list_data:
        data_final = pd.concat(list_data).reset_index(drop=True)

        _warning_get_data()

        return SireneDataFrame(data_final)

    raise ValueError("!!! No data found for the provided identifiers !!!")
