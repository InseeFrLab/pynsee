# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
import xml.etree.ElementTree as ET
import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def _get_dataset_dimension(
    dataset, update=False, silent=False, insee_date_test=None
):

    INSEE_sdmx_link_datastructure = (
        "https://bdm.insee.fr/series/sdmx/datastructure/FR1"
    )
    INSEE_api_link_datastructure = (
        "https://api.insee.fr/series/BDM/V1/datastructure/FR1"
    )

    INSEE_sdmx_link_datastructure_dataset = (
        INSEE_sdmx_link_datastructure + "/" + dataset
    )
    INSEE_api_link_datastructure_dataset = (
        INSEE_api_link_datastructure + "/" + dataset
    )

    with PynseeAPISession() as session:
        results = session.request_insee(
            sdmx_url=INSEE_sdmx_link_datastructure_dataset,
            api_url=INSEE_api_link_datastructure_dataset,
        )

    dataset_dimension_file = io.BytesIO(results.content)

    root = ET.parse(dataset_dimension_file).getroot()

    data = root[1][0][0][2][0]

    n_dimension = len(data)

    list_dimension = []

    def extract_local_rep(data, i):
        try:
            local_rep = next(iter(data[i][1][0][0].attrib.values()))
        except Exception:
            local_rep = None

        return local_rep

    def extract_id(data, i):
        try:
            id_val = next(iter(data[i].attrib.values()))
        except Exception:
            id_val = None

        return id_val

    for i in range(0, n_dimension):
        dimension_id = extract_id(data, i)
        local_rep = extract_local_rep(data, i)

        dimension_df = {
            "dataset": [dataset],
            "dimension": [dimension_id],
            "local_representation": [local_rep],
        }

        dimension_df = pd.DataFrame(
            dimension_df,
            columns=["dataset", "dimension", "local_representation"],
        )

        list_dimension.append(dimension_df)

    dimension_df_all = pd.concat(list_dimension)
    dimension_df_all = dimension_df_all.dropna()

    return dimension_df_all
