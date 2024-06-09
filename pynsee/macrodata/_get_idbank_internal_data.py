# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import zipfile
import pkg_resources
import pandas as pd
import os

from pynsee.utils.save_df import save_df
from pynsee.utils._get_temp_dir import _get_temp_dir

import logging

logger = logging.getLogger(__name__)

@save_df(day_lapse_max=90)
def _get_idbank_internal_data(update=False, silent=True):
    
    zip_file = pkg_resources.resource_stream(
        __name__, "data/idbank_list_internal.zip"
    )

    temp_folder = _get_temp_dir()
    data_file = os.path.join(temp_folder, "idbank_list_internal.csv")

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    idbank_list = pd.read_csv(
        data_file, encoding="utf-8", quotechar='"', sep=",", dtype=str
    )

    return idbank_list
