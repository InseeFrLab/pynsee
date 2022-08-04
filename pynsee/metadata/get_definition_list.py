# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
from pynsee.utils._request_insee import _request_insee
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict

import zipfile
import os
import pkg_resources
import pandas as pd


@lru_cache(maxsize=None)
def _warning_definition_internal_data():
    msg1 = "!!! Internal package data has been used !!!\n!!! If some data is missing, please use get_definition !!!"
    print(msg1)


@lru_cache(maxsize=None)
def get_definition_list():
    """Get a list of concept definitions

    Examples:
        >>> from pynsee.metadata import get_definition_list
        >>> definition = get_definition_list()
    """

    insee_folder = _create_insee_folder()

    insee_folder_local_def = insee_folder + "/" + "definition"

    if not os.path.exists(insee_folder_local_def):
        os.mkdir(insee_folder_local_def)

    list_expected_files = ["all_definitions.csv"]

    list_expected_files = [
        insee_folder + "/definition/" + f for f in list_expected_files
    ]

    list_available_file = [not os.path.exists(f) for f in list_expected_files]

    # unzipping raw files
    if any(list_available_file):

        zip_file = pkg_resources.resource_stream(__name__, "data/definition.zip")

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(insee_folder)

    link = "https://api.insee.fr/metadonnees/V1/concepts/definitions"

    request = _request_insee(api_url=link, file_format="application/json")

    data_request = request.json()

    list_data = []

    for i in range(len(data_request)):
        df = _make_dataframe_from_dict(data_request[i])
        df = df.iloc[:, 0:3].reset_index(drop=True).drop_duplicates()
        list_data.append(df)

    data = pd.concat(list_data, axis=0)
    data = data.reset_index(drop=True)
    data.columns = ["ID", "URI", "TITLE_FR"]

    if os.path.exists(list_expected_files[0]):
        all_data = pd.read_csv(list_expected_files[0])
        all_data = all_data.iloc[:, 1:10]
        all_data = all_data.drop(columns={"URI", "TITLE_FR"})
        data = data.merge(all_data, on="ID", how="left")

    _warning_definition_internal_data()

    return data
