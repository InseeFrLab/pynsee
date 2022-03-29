# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache

from pynsee.macrodata._get_idbank_internal_data_harmonized import _get_idbank_internal_data_harmonized
from pynsee.macrodata._get_idbank_internal_data import _get_idbank_internal_data
from pynsee.macrodata.get_series_list import get_series_list

@lru_cache(maxsize=None)
def search_macrodata(pattern=".*", metadata=True):
    """Search a pattern among insee series (idbanks)

    Notes:
        This function uses package's internal data which might not be the most up-to-date.

    Args:
        pattern (str, optional): String used to filter the idbank list. Defaults to ".*", returns all series.

    Examples:
        >>> from pynsee.macrodata import search_macrodata
        >>> search_all = search_macrodata()
        >>> search_paper = search_macrodata("pâte à papier")
        >>> search_paris = search_macrodata("PARIS")
        >>> search_survey_gdp = search_macrodata("Survey|GDP")
    """

    if pattern not in [".*", ""]:
        idbank_list = _get_idbank_internal_data_harmonized()

        pattern = str(pattern).lower()

        idbank_selected = idbank_list.loc[
            idbank_list.title_en_lower.str.contains(pattern)
            | idbank_list.title_fr_lower.str.contains(pattern)
            | idbank_list.title_fr_no_accent.str.contains(pattern)]

    else:
        idbank_selected = _get_idbank_internal_data()

    idbank_selected = idbank_selected[[
        "DATASET", "IDBANK", "KEY", "TITLE_FR", "TITLE_EN"]]

    if metadata:
        try:
            list_dataset = list(idbank_selected.DATASET.unique())
            metata_df = get_series_list(list_dataset)
            newcol = [col for col in metata_df.columns if col not in idbank_selected.columns] + ['IDBANK']
            metata_df = metata_df[newcol]

            idbank_selected = idbank_selected.merge(metata_df, on='IDBANK', how='left')
            # remove all na columns
            idbank_selected = idbank_selected.dropna(axis=1, how='all')
        except:
            pass


    return(idbank_selected)
