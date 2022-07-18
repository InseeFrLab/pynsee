# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._get_temp_dir import _get_temp_dir
from pynsee.utils._hash import _hash
from pynsee.utils._request_insee import _request_insee


def _get_dataset_dimension(dataset, update=False):

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

    insee_folder = _create_insee_folder()
    file = insee_folder + "/" + _hash(INSEE_sdmx_link_datastructure_dataset)

    trigger_update = update

    # if the data is not saved locally, or if it is too old (>90 days)
    # then an update is triggered

    if not os.path.exists(file):
        trigger_update = True
    else:
        try:
            # only used for testing purposes
            insee_date_time_now = os.environ["insee_date_test"]
            insee_date_time_now = datetime.strptime(
                insee_date_time_now, "%Y-%m-%d %H:%M:%S.%f"
            )
        except:
            insee_date_time_now = datetime.now()

        # file date creation
        file_date_last_modif = datetime.fromtimestamp(os.path.getmtime(file))
        day_lapse = (insee_date_time_now - file_date_last_modif).days

        if day_lapse > 90:
            trigger_update = True

    if trigger_update:

        results = _request_insee(
            sdmx_url=INSEE_sdmx_link_datastructure_dataset,
            api_url=INSEE_api_link_datastructure_dataset,
        )

        # create temporary directory
        dirpath = _get_temp_dir()

        dataset_dimension_file = dirpath + "\\dataset_dimension_file"

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

        # save data
        dimension_df_all.to_pickle(file)

    else:
        # pickle format depends on python version
        # then read_pickle can fail, if so
        # the file is removed and the function is launched again
        # testing requires multiple python versions
        try:
            dimension_df_all = pd.read_pickle(file)
        except:
            os.remove(file)
            dimension_df_all = _get_dataset_dimension(dataset)

    return dimension_df_all
