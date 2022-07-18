# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
import re

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata._get_dataset_metadata import _get_dataset_metadata


def get_series_list(*datasets, update=False):
    """Download an INSEE's series key list for one or several datasets from BDM macroeconomic database

    Args:
        datasets (str) : datasets should be among the datasets list provided by get_dataset_list()

        update (bool, optional): Set to True, to update manually the metadata
        stored locally on the computer. Defaults to False.

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
    insee_dataset = get_dataset_list()
    insee_dataset_list = insee_dataset["id"].to_list()

    if len(datasets) == 1:
        if isinstance(datasets[0], list):
            datasets = datasets[0]

    for dt in datasets:
        if dt not in insee_dataset_list:
            raise ValueError(
                "\n%s is not a dataset from INSEE\nGet a dataset list with get_dataset_list function"
                % dt
            )

    idbank_list_dataset = []

    for dt in datasets:
        idbank_list_dt = _get_dataset_metadata(dt, update=update)

        idbank_list_dataset.append(idbank_list_dt)

    idbank_list = pd.concat(idbank_list_dataset)

    # label columns at the end

    r = re.compile(".*_label_.*")
    column_all = idbank_list.columns.to_list()
    column_label = list(filter(r.match, column_all))
    column_other = [col for col in column_all if col not in column_label]
    new_column_order = column_other + column_label

    idbank_list = pd.DataFrame(idbank_list, columns=new_column_order)

    idbank_list = idbank_list.rename(
        columns={"nomflow": "DATASET", "idbank": "IDBANK", "cleFlow": "KEY"}
    )

    idbank_list.columns = [col.replace("-", "_") for col in idbank_list.columns]

    return idbank_list
