# -*- coding: utf-8 -*-

from pandas import DataFrame

from pynsee.utils.save_df import save_df

from ._get_full_list_wfs import _get_full_list_wfs


@save_df(day_lapse_max=90)
def get_geodata_list(update=False, silent=False) -> DataFrame:
    """Get a list of geographical limits of French administrative areas from IGN API

    Args:
        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False.

        silent (bool, optional): Set to True, to disable messages printed in log info

    Examples:
        >>> from pynsee.geodata import get_geodata_list
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
    """

    format = "WFS"
    topic = "administratif"
    version = "2.0.0"

    data_full_list = _get_full_list_wfs(topic=topic, version=version)

    if len(data_full_list) > 0:
        list_var = [
            "Name",
            "Identifier",
            "Title",
            "DefaultCRS",
            "SupportedCRS",
            "TileMatrixSet",
            "Abstract",
            "LegendURL",
            "Format",
        ]

        list_first_col = [
            col for col in data_full_list.columns if col in list_var
        ]
        list_other_col = [
            col for col in data_full_list.columns if col not in list_first_col
        ]

        data_list = data_full_list[list_first_col + list_other_col]
        data_list = data_list.drop_duplicates().reset_index(drop=True)

        if "Name" in data_list.columns:
            data_list.rename(columns={"Name": "Identifier"}, inplace=True)

        data_list["DataFormat"] = format
        data_list["ApiVersion"] = version

    data_all = data_list.reset_index(drop=True)

    # set column order
    first_col = [
        "Topic",
        "DataFormat",
        "ApiVersion",
        "Identifier",
        "Abstract",
        "Title",
        "ZoomRange",
    ]
    available_col = [col for col in first_col if col in data_all.columns]
    other_col = [col for col in data_all.columns if col not in available_col]

    data_all = data_all[available_col + other_col]

    return data_all
