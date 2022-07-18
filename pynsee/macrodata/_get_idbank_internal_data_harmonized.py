# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import unidecode
import pandas as pd

from ._get_idbank_internal_data import _get_idbank_internal_data


@lru_cache(maxsize=None)
def _get_idbank_internal_data_harmonized():

    idbank_list = _get_idbank_internal_data()

    col_selected = ["DATASET", "IDBANK", "KEY", "TITLE_FR", "TITLE_EN"]
    idbank_col_selected = idbank_list.columns[idbank_list.columns.isin(col_selected)]
    idbank_list = idbank_list[idbank_col_selected]

    # all titles in lower case
    title_fr_lower = pd.Series(
        [str(title).lower() for title in idbank_list["TITLE_FR"]]
    )
    idbank_list = idbank_list.assign(title_fr_lower=title_fr_lower.values)

    title_en_lower = pd.Series(
        [str(title).lower() for title in idbank_list["TITLE_EN"]]
    )
    idbank_list = idbank_list.assign(title_en_lower=title_en_lower.values)

    # create column without accent
    title_fr_no_accent = [
        unidecode.unidecode(str(title)) for title in idbank_list["title_fr_lower"]
    ]
    title_fr_no_accent = pd.Series(title_fr_no_accent)
    idbank_list = idbank_list.assign(title_fr_no_accent=title_fr_no_accent.values)

    return idbank_list
