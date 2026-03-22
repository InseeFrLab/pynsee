# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import functools
import logging

import pandas as pd

from ..utils.save_df import save_df
from ._download_idbanks import _download_idbank_list
from ._get_dimensions import _get_dataset_dimension, _get_dimension_values
from ._get_idbank_internal_data import _get_idbank_internal_data


logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=None)
def _warning_error():
    logger.error(
        "Package's internal data has been used !\n"
        "Idbank file download failed, have a look at the following page "
        "and find the new link !\n"
        "https://www.insee.fr/en/information/2868055\n\n"
        "You may change the downloaded file changing the following "
        "environment variable !\n"
        "import os; os.environ['pynsee_idbank_file'] = 'my_new_idbank_file'\n"
        "Please contact the package maintainer if this error persists !"
    )


@save_df(day_lapse_max=90)
def _get_dataset_metadata(
    dataset, update=False, silent=False, insee_date_test=None
):
    """Get dataset metadata; use local data as backup if server fails."""
    try:
        idbank_list_dataset = _get_dataset_metadata_core(
            dataset=dataset, update=update, silent=silent
        )
    except Exception:
        # if the download of the idbank file and the build of the metadata fail
        # package's internal data is provided to the user, should be
        # exceptional, used as a backup
        _warning_error()

        idbank_list_dataset = _get_idbank_internal_data(update=update)
        idbank_list_dataset = idbank_list_dataset[
            idbank_list_dataset["DATASET"] == dataset
        ]

        # drop the columns where all elements are NaN
        idbank_list_dataset = idbank_list_dataset.dropna(axis=1, how="all")
        idbank_list_dataset = idbank_list_dataset.reset_index(drop=True)

    return idbank_list_dataset


@save_df(day_lapse_max=90)
def _get_dataset_metadata_core(dataset, update=False, silent=False):
    """Get metadata from idbanks"""
    idbank_list = _download_idbank_list(update=update, silent=silent)

    # get dataset's dimensions
    dataset_dimension = _get_dataset_dimension(
        dataset, update=update, silent=silent
    ).reset_index(drop=True)

    # select only the idbanks corresponding to the dataset
    idbank_list_dataset = idbank_list[
        idbank_list["nomflow"] == dataset
    ].reset_index(drop=True)

    # split the cleflow column with the dot as a separator
    df_cleflow_splitted = idbank_list_dataset.cleFlow.str.split("\\.").tolist()

    # map the original to the new column names
    convertor = {
        row.local_representation[3:]: row.dimension
        for _, row in dataset_dimension.iterrows()
    }

    colnames = idbank_list_dataset.iloc[0].list_var.split(".")

    new_columns = [convertor[c] for c in colnames]

    # make a dataframe from the splitted cleflow using the new column names
    df_cleflow_splitted = pd.DataFrame(
        df_cleflow_splitted, columns=new_columns
    )

    # join the splitted cleflow dataframe with the former idbank list
    idbank_list_dataset = pd.concat(
        [idbank_list_dataset, df_cleflow_splitted], axis=1
    )

    for irow, dim_id in dataset_dimension["dimension"].items():
        if dim_id not in idbank_list_dataset.columns:
            continue

        dim_local_rep = dataset_dimension["local_representation"].iloc[irow]

        # get dimension values
        dim_values = _get_dimension_values(
            dim_local_rep, update=update, silent=silent
        )

        # drop dimension label
        dim_values = dim_values[dim_values["id"] != dim_local_rep]

        # rename columns
        dim_values.columns = [
            dim_id,
            dim_id + "_label_fr",
            dim_id + "_label_en",
        ]
        idbank_list_dataset = idbank_list_dataset.merge(
            dim_values, on=dim_id, how="left"
        )

    return idbank_list_dataset.drop(columns=["list_var"])
