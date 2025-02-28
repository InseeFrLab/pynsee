# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
import logging
import xml.etree.ElementTree as ET

import pandas as pd
from tqdm import trange

from ..utils.requests_session import PynseeAPISession
from ..utils.save_df import save_df
from ._get_dataset_list_internal import _get_dataset_list_internal


logger = logging.getLogger(__name__)


@save_df(day_lapse_max=30)
def get_dataset_list(update=False, silent=False):
    """Download a full INSEE's datasets list from BDM macroeconomic database

    Args:
        update (bool, optional): Set to True, to update manually the metadata
        stored locally on the computer. Defaults to False.

        silent (bool, optional): Set to True, to disable messages printed in log info

    Returns:
        DataFrame: a dataframe containing the list of datasets available

    Examples:
        >>> from pynsee.macrodata import get_dataset_list
        >>> insee_dataset = get_dataset_list()
    """

    try:

        INSEE_sdmx_link_dataflow = "https://bdm.insee.fr/series/sdmx/dataflow"
        INSEE_api_link_dataflow = (
            "https://api.insee.fr/series/BDM/dataflow/FR1/all"
        )

        with PynseeAPISession() as session:
            results = session.request_insee(
                sdmx_url=INSEE_sdmx_link_dataflow,
                api_url=INSEE_api_link_dataflow,
            )

        dataflow_file = io.BytesIO(results.content)
        root = ET.parse(dataflow_file).getroot()

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
                dataset,
                columns=["id", "Name.fr", "Name.en", "url", "n_series"],
            )
            list_df.append(dt)

        # concatenate list of dataframes
        df = pd.concat(list_df)

        # clean up columns
        df = df.astype(str)

        df["n_series"] = df["n_series"].str.replace("\\D", "", regex=True)
        df["n_series"] = df["n_series"].astype("int")

        df = df[df["id"] != "SERIES_BDM"]

        df["Name.en"] = df["Name.en"].str.replace(
            "^\\n\\s{0,}", "", regex=True
        )
        df["Name.fr"] = df["Name.fr"].str.replace(
            "^\\n\\s{0,}", "", regex=True
        )
        df = df[df["Name.en"] != ""]
        df = df[df["Name.fr"] != ""]

    except Exception:
        df = _get_dataset_list_internal()

        logger.error(
            "Package's internal data has been used !\n"
            "Dataset list download failed !"
            "Please contact the package maintainer if this error persists !"
        )

    df = df.reset_index(drop=True)

    return df
