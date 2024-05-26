# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import xml.etree.ElementTree as ET
import pandas as pd
import os

from pynsee.utils._get_temp_dir import _get_temp_dir
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.save_df import save_df

@save_df(day_lapse_max=90)
def _get_dataset_dimension(dataset, update=False, silent=True, insee_date_test=None):

    INSEE_sdmx_link_datastructure = (
        "https://www.bdm.insee.fr/series/sdmx/datastructure/FR1"
    )
    INSEE_api_link_datastructure = (
        "https://api.insee.fr/series/BDM/V1/datastructure/FR1"
    )

    INSEE_sdmx_link_datastructure_dataset = (
        INSEE_sdmx_link_datastructure + "/" + dataset
    )
    INSEE_api_link_datastructure_dataset = INSEE_api_link_datastructure + "/" + dataset

    results = _request_insee(
        sdmx_url=INSEE_sdmx_link_datastructure_dataset,
        api_url=INSEE_api_link_datastructure_dataset,
    )

    # create temporary directory
    dirpath = _get_temp_dir()

    dataset_dimension_file = os.path.join(dirpath, "dataset_dimension_file")

    with open(dataset_dimension_file, "wb") as f:
        f.write(results.content)

    root = ET.parse(dataset_dimension_file).getroot()

    data = root[1][0][0][2][0]

    n_dimension = len(data)

    list_dimension = []

    def extract_local_rep(data, i):
        try:
            local_rep = next(iter(data[i][1][0][0].attrib.values()))
        except:
            local_rep = None
        finally:
            return local_rep

    def extract_id(data, i):
        try:
            id_val = next(iter(data[i].attrib.values()))
        except:
            id_val = None
        finally:
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
            dimension_df, columns=["dataset", "dimension", "local_representation"]
        )

        list_dimension.append(dimension_df)

    dimension_df_all = pd.concat(list_dimension)
    dimension_df_all = dimension_df_all.dropna()

    return dimension_df_all
