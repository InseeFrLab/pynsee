# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.macrodata._get_dimension_values import _get_dimension_values


def _add_numeric_metadata(data):

    # data = get_dataset('CLIMAT-AFFAIRES')

    list_numeric_col_metadata = [
        "OBS_STATUS",
        "OBS_REV",
        "OBS_CONF",
        "OBS_TYPE",
        "OBS_QUAL",
    ]

    for col in list_numeric_col_metadata:
        cl_col = "CL_" + col
        df = _get_dimension_values(cl_col)

        df = df[df["id"] != cl_col]

        # rename columns
        df.columns = [col, col + "_label_fr", col + "_label_en"]

        if col in data.columns:
            data = data.merge(df, on=col, how="left")

    return data
