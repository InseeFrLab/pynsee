# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd

from pynsee.macrodata._download_idbank_list import _download_idbank_list
from pynsee.macrodata._get_dataset_dimension import _get_dataset_dimension
from pynsee.macrodata._get_dimension_values import _get_dimension_values
from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def _get_dataset_metadata_core(dataset, update=False, silent=False):

    idbank_list = _download_idbank_list(
        update=update, silent=silent, include_list_var=True
    )

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

    n_dimensions = len(dataset_dimension.index)

    for irow in range(n_dimensions):
        dim_id = dataset_dimension["dimension"].iloc[irow]
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

        if dim_id in idbank_list_dataset.columns:
            idbank_list_dataset = idbank_list_dataset.merge(
                dim_values, on=dim_id, how="left"
            )

    return idbank_list_dataset.drop(columns=["list_var"])
