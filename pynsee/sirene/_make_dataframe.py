# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from tqdm import tqdm

import pynsee
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict


def _make_dataframe(data_request, main_key, query_number):

    list_dataframe = []

    try:
        data = data_request[main_key]
    except Exception:
        main_key_list = [key for key in list(data_request.keys()) if key != "header"]
        main_key = main_key_list[0]
        data = data_request[main_key]

    for elt in tqdm(
        data, desc="{} - Getting data".format(query_number),
        disable=pynsee.get_config("hide_progress")
    ):
        data_final = _make_dataframe_from_dict(elt)

        list_dataframe.append(data_final)

    data_final = pd.concat(list_dataframe)

    return data_final
