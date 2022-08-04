# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from functools import lru_cache
from tqdm import trange
from pynsee.utils._hash import _hash
from pynsee.utils._create_insee_folder import _create_insee_folder
import os

from pynsee.utils._request_insee import _request_insee


@lru_cache(maxsize=None)
def _warning_legaldata_save():
    print(
        f"Locally saved legal data has been used\nSet update=True to trigger an update"
    )


def get_legal_entity(codes, print_err_msg=True, update=False):
    """Get legal entities labels

    Args:
        codes (list): list of legal entities code of 2 or 4 characters

    Examples:
        >>> from pynsee.metadata import get_legal_entity
        >>> legal_entity = get_legal_entity(codes = ['5599', '83'])
    """

    filename = _hash("get_legal_entity" + "".join(codes))
    insee_folder = _create_insee_folder()
    file_legal_entity = insee_folder + "/" + filename

    if (not os.path.exists(file_legal_entity)) or update:

        list_data = []

        for c in trange(len(codes), desc="Getting legal entities"):
            # c = '5599'
            code = codes[c]
            try:
                data = _get_one_legal_entity(code, print_err_msg=print_err_msg)
                list_data.append(data)
            except:
                pass

        data_final = pd.concat(list_data).reset_index(drop=True)

        data_final = data_final.rename(columns={"intitule": "title"})
        data_final.to_pickle(file_legal_entity)
        print(f"Data saved: {file_legal_entity}")

    else:
        try:
            data_final = pd.read_pickle(file_legal_entity)
        except:
            os.remove(file_legal_entity)

            data_final = get_legal_entity(
                codes=codes, print_err_msg=print_err_msg, update=True
            )

        else:
            _warning_legaldata_save()

    return data_final


@lru_cache(maxsize=None)
def _get_one_legal_entity(c, print_err_msg=True):

    if len(c) == 2:
        n = "n2"
    elif len(c) == 4:
        n = "n3"
    else:
        raise ValueError("!!! Legal entity code should have 2 or 4 charaters !!!")

    INSEE_legal_entity_n3 = "https://api.insee.fr/metadonnees/V1/codes/cj/" + n + "/"

    request = _request_insee(
        api_url=INSEE_legal_entity_n3 + c,
        file_format="application/json;charset=utf-8",
        print_msg=print_err_msg,
    )

    data_request = request.json()

    data = pd.DataFrame(data_request, index=[0])

    return data
