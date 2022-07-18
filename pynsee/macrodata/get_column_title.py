# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from tqdm import trange

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata._get_dataset_dimension import _get_dataset_dimension
from pynsee.macrodata._get_dimension_values import _get_dimension_values


def get_column_title(dataset=None):
    """Get the title of a dataset's columns

    Args:
        dataset (str, optional): An INSEE dataset name. Defaults to None, this returns all columns.

    Raises:
        ValueError: Only one string (length one)
        ValueError: Dataset must belong to INSEE datasets list

    Examples:
        >>> from pynsee.macrodata import get_column_title
        >>> insee_all_columns = get_column_title()
        >>> balance_paiements_columns = get_column_title("BALANCE-PAIEMENTS")
    """

    insee_dataset = get_dataset_list()
    insee_dataset_list = insee_dataset["id"].to_list()

    if dataset is None:
        dataset_list = insee_dataset_list
    else:
        for dt in dataset:
            if dt not in insee_dataset_list:
                raise ValueError("%s is not a dataset from INSEE" % dt)
        dataset_list = dataset

    # make a list of all columns
    list_column = []

    n_dataset = len(dataset_list)

    for idt in trange(n_dataset, desc="1/2 - Getting columns list "):
        dt = dataset_list[idt]
        dataset_dimension = _get_dataset_dimension(dt)
        dataset_dimension = dataset_dimension[["dimension", "local_representation"]]
        list_column.append(dataset_dimension)

    df_column = pd.concat(list_column)
    df_column = df_column.drop_duplicates()

    list_column = []
    n_dimensions = len(df_column.index)

    for irow in trange(n_dimensions, desc="2/2 - Getting values "):
        dim_id = df_column["dimension"].iloc[irow]
        dim_id = str(dim_id).replace("-", "_")
        dim_local_rep = df_column["local_representation"].iloc[irow]

        dim_values = _get_dimension_values(dim_local_rep)

        # drop dimension label
        dim_values = dim_values[dim_values["id"] == dim_local_rep]

        # new column with the dimension id
        dim_values = dim_values.assign(
            column=pd.Series(
                dim_id * len(dim_values.index), index=dim_values.index
            ).values
        )
        dim_values = dim_values[["column", "name_fr", "name_en"]]
        list_column.append(dim_values)

    df_column_final = pd.concat(list_column).reset_index(drop=True)
    return df_column_final
