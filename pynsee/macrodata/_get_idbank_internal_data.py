# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
import zipfile
import importlib
import pandas as pd

from pynsee.utils.save_df import save_df

import logging

logger = logging.getLogger(__name__)


@save_df(day_lapse_max=90)
def _get_idbank_internal_data(update=False, silent=False):

    try:
        pkg_macrodata = importlib.resources.files(__name__)
        zip_file = str(pkg_macrodata) + "/data/idbank_list_internal.zip"
    except Exception:
        import pkg_resources

        zip_file = pkg_resources.resource_stream(
            __name__, "data/idbank_list_internal.zip"
        )

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        data_file = io.BytesIO(zip_ref.read("idbank_list_internal.csv"))

    idbank_list = pd.read_csv(
        data_file, encoding="utf-8", quotechar='"', sep=",", dtype=str
    )

    col = "Unnamed: 0"
    if col in idbank_list.columns:
        idbank_list = idbank_list.drop(columns={col})

    return idbank_list
