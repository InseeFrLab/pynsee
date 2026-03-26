# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import re

import pandas as pd

from ..utils.save_df import save_df
from ._get_metadata import _get_dataset_metadata
from .get_dataset_list import get_dataset_list


@save_df(day_lapse_max=30)
def get_series_list(*datasets, update=False, silent=False):
    """Download an INSEE's series key list for one or several datasets from BDM macroeconomic database

    Args:
        datasets (str) : datasets should be among the datasets list provided by get_dataset_list()

        update (bool, optional): Set to True, to update manually the metadata
        stored locally on the computer. Defaults to False.

        silent (bool, optional): Set to True, to disable messages printed in log info

    Raises:
        ValueError: datasets should be among the datasets list provided by get_dataset_list()

    Returns:
        DataFrame: contains dimension columns, series keys, dataset name

    Notes:
        Some metadata is stored for 3 months locally on the computer. It is updated automatically

    Examples:
        >>> from pynsee.macrodata import get_dataset_list, get_series_list
        >>> dataset_list = get_dataset_list()
        >>> idbank_ipc = get_series_list('IPC-2015', 'CLIMAT-AFFAIRES')
    """
    insee_dataset = get_dataset_list(silent=silent, update=update)
    all_datasets = set(insee_dataset["id"])

    if len(datasets) == 1:
        if isinstance(datasets[0], list):
            datasets = datasets[0]

    wrong_datasets = [ds for ds in datasets if ds not in all_datasets]

    if wrong_datasets:
        raise ValueError(
            "The following are not datasets from INSEE: "
            f"{', '.join(wrong_datasets)}.\n"
            "Get a dataset list from the `get_dataset_list` function."
        )

    # get all datasets
    df = pd.concat(
        [
            _get_dataset_metadata(dt, update=update, silent=silent)
            for dt in datasets
        ],
        ignore_index=True,
    )

    # put label columns at the end and set names properly
    r = re.compile(".*_label_.*")
    column_all = df.columns.to_list()
    column_label = list(filter(r.match, column_all))
    column_other = [col for col in column_all if col not in column_label]
    new_column_order = column_other + column_label

    df = df.reindex(columns=new_column_order).rename(
        columns={"nomflow": "DATASET", "idbank": "IDBANK", "cleFlow": "KEY"}
    )

    df.columns = [col.replace("-", "_") for col in df.columns]

    return df
