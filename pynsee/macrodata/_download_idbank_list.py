# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from typing import Optional
from datetime import datetime


from pynsee.macrodata._dwn_idbank_files import _dwn_idbank_files

from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def _download_idbank_list(
    update: bool = False,
    silent: bool = False,
    insee_date_test: Optional[datetime] = None,
    include_list_var: bool = False,
):

    data = _dwn_idbank_files()

    columns = ["nomflow", "idbank", "cleFlow"]

    if not include_list_var:
        data = data.iloc[:, 0:3]
    else:
        columns.append("list_var")

    data.columns = columns

    data = data.sort_values("nomflow").reset_index(drop=True)

    return data
