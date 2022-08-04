# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import os
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import trange

from pynsee.macrodata._get_dataset_list_internal import _get_dataset_list_internal
from pynsee.utils._request_insee import _request_insee
from pynsee.utils._get_temp_dir import _get_temp_dir


@lru_cache(maxsize=None)
def get_dataset_list():
    """Download a full INSEE's datasets list from BDM macroeconomic database

    Returns:
        DataFrame: a dataframe containing the list of datasets available

    Examples:
        >>> from pynsee.macrodata import get_dataset_list
        >>> insee_dataset = get_dataset_list()
    """

    try:

        INSEE_sdmx_link_dataflow = "https://bdm.insee.fr/series/sdmx/dataflow"
        INSEE_api_link_dataflow = "https://api.insee.fr/series/BDM/V1/dataflow/FR1/all"

        results = _request_insee(
            api_url=INSEE_api_link_dataflow, sdmx_url=INSEE_sdmx_link_dataflow
        )

        # create temporary directory
        dirpath = _get_temp_dir()

        dataflow_file = dirpath + "\\dataflow_file"

        with open(dataflow_file, "wb") as f:
            f.write(results.content)

        root = ET.parse(dataflow_file).getroot()

        if os.path.exists(dataflow_file):
            os.remove(dataflow_file)

        data = root[1][0]

        n_dataflow = len(data)

        list_df = []

        for i in trange(n_dataflow, desc="Getting datasets list"):

            dataset = {
                "id": [next(iter(data[i].attrib.values()))],
                "Name.fr": [data[i][1].text],
                "Name.en": [data[i][2].text],
                "url": [data[i][0][0][0].text],
                "n_series": [data[i][0][1][0].text],
            }

            dt = pd.DataFrame(
                dataset, columns=["id", "Name.fr", "Name.en", "url", "n_series"]
            )
            list_df.append(dt)

        # concatenate list of dataframes
        df = pd.concat(list_df)

        # clean up columns
        df = df.astype(str)

        df["n_series"] = df["n_series"].str.replace("\\D", "", regex=True)
        df["n_series"] = df["n_series"].astype("int")

        df = df[df["id"] != "SERIES_BDM"]

        df["Name.en"] = df["Name.en"].str.replace("^\\n\\s{0,}", "", regex=True)
        df["Name.fr"] = df["Name.fr"].str.replace("^\\n\\s{0,}", "", regex=True)
        df = df[df["Name.en"] != ""]
        df = df[df["Name.fr"] != ""]

    except:
        df = _get_dataset_list_internal()

        print("\n!!! Package's internal data has been used !!!\n")
        print("!!! Dataset list download failed !!!")
        print("!!! Please contact the package maintainer if this error persists !!!")

    df = df.reset_index(drop=True)

    return df
