# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from functools import lru_cache
from tqdm import trange

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=30)
def get_legal_entity(codes, print_err_msg=True, update=False, silent=False):
    """Get legal entities labels

    Args:
        codes (list): list of legal entities code of 2 or 4 characters

        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False

        silent (bool, optional): Set to True, to disable messages printed in log info

    Examples:
        >>> from pynsee.metadata import get_legal_entity
        >>> legal_entity = get_legal_entity(codes = ['5599', '83'])
    """

    list_data = []

    for c in trange(len(codes), desc="Getting legal entities"):
        # c = '5599'
        code = codes[c]
        try:
            data = _get_one_legal_entity(code, print_err_msg=print_err_msg)
            list_data.append(data)
        except Exception:
            pass

    data_final = pd.concat(list_data).reset_index(drop=True)

    data_final = data_final.rename(columns={"intitule": "title"})

    return data_final


@lru_cache(maxsize=None)
def _get_one_legal_entity(c, print_err_msg=True):
    if len(c) == 2:
        n = "n2"
    elif len(c) == 4:
        n = "n3"
    else:
        raise ValueError(
            "!!! Legal entity code should have 2 or 4 charaters !!!"
        )

    INSEE_legal_entity_n3 = (
        "https://api.insee.fr/metadonnees/codes/cj/" + n + "/"
    )

    with PynseeAPISession() as session:
        request = session.request_insee(
            api_url=INSEE_legal_entity_n3 + c,
            file_format="application/json;charset=utf-8",
            print_msg=print_err_msg,
        )

    data_request = request.json()

    data = pd.DataFrame(data_request, index=[0])

    return data
