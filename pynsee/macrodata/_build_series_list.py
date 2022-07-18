# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata.get_series_list import get_series_list
from pynsee.macrodata.get_series_title import get_series_title
from pynsee.macrodata.search_macrodata import search_macrodata
from tqdm import trange
import os
import pandas as pd


def _build_series_list(dt=["CNA-2014-ERE"]):

    #
    # FIRST change the link, file name and separator in _download_idbank_list
    # THEN build the package and try to use the following to make a new idbank_list file
    # FINALLY put the file in the zip file in macrodata/data
    #

    #
    # SET dt = None TO BUILD THE FULL DATAFRAME
    #

    # os.environ['pynsee_query_print']= "True"
    os.environ["pynsee_use_sdmx"] = "True"

    if dt is None:
        dt = get_dataset_list()
        dt = dt.id.to_list()

    list_dt = []

    for d in trange(len(dt)):
        dataset = dt[d]
        df = get_series_list(dataset, update=True)
        list_dt.append(df)

    series_list = pd.concat(list_dt)
    # series_list.to_csv("pynsee_series_all.csv")
    # series_list = pd.read_csv("../pynsee_series_all.csv", dtype=str)
    # col = 'Unnamed: 0'
    # series_list = series_list.drop(columns = {col})

    old_series = search_macrodata()
    old_series = old_series.drop(columns={"KEY"})
    series_list_short = series_list[["DATASET", "IDBANK", "KEY"]]

    series_list_new = series_list_short.merge(
        old_series, on=["DATASET", "IDBANK"], how="left"
    )

    series_list_new_title_missing = series_list_new[
        pd.isna(series_list_new["TITLE_FR"])
    ]
    series_list_new_title_missing = series_list_new_title_missing.drop(
        columns={"TITLE_FR", "TITLE_EN"}
    )

    list_series_title_missing = series_list_new_title_missing.IDBANK.to_list()

    if len(list_series_title_missing) > 0:
        titles = get_series_title(list_series_title_missing)

        # !!!!!!!!!!!!!!!!!!!!!!
        # SERIES IN IDBANK FILE NOT AVAILABLE IN BDM DATABASE
        # !!!!!!!!!!!!!!!!!!!!!!
        # series_not_found = [l for l in list_series_title_missing if l not in titles.IDBANK.to_list()]

        if len(titles.index) > 0:
            titles = titles.rename(
                columns={"TITLE_FR": "TITLE_FR2", "TITLE_EN": "TITLE_EN2"}
            )

            series_list_new2 = series_list_new.merge(titles, on="IDBANK", how="left")

            for i in range(len(series_list_new2.index)):
                tt_fr = series_list_new2.loc[i, "TITLE_FR"]
                tt_en = series_list_new2.loc[i, "TITLE_EN"]
                if pd.isna(tt_fr):
                    series_list_new2.loc[i, "TITLE_FR"] = series_list_new2.loc[
                        i, "TITLE_FR2"
                    ]

                if pd.isna(tt_en):
                    series_list_new2.loc[i, "TITLE_EN"] = series_list_new2.loc[
                        i, "TITLE_EN2"
                    ]

            series_list_new2 = series_list_new2.drop(columns={"TITLE_FR2", "TITLE_EN2"})
            # series_not_found2 = series_list_new2[pd.isna(series_list_new2['TITLE_FR'])]
            series_list_new2 = series_list_new2.dropna(subset={"TITLE_FR"})
            series_list_new2 = series_list_new2[["IDBANK", "TITLE_FR", "TITLE_EN"]]

            series_list2 = series_list.merge(series_list_new2, on="IDBANK", how="right")

            # !!!!!!!!!
            # CREATE FILE FOR PACKAGE INTERNAL DATA
            # !!!!!!!!!
            # series_list2.to_csv("idbank_list_internal.csv", encoding = "utf-8", quotechar='"', sep=',')

        os.environ["pynsee_use_sdmx"] = "False"
        return series_list2
    else:
        os.environ["pynsee_use_sdmx"] = "False"
        return old_series
