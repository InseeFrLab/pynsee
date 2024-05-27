# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
import os

from pynsee.macrodata._dwn_idbank_files import _dwn_idbank_files

from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils.save_df import save_df

@save_df(day_lapse_max=90)
def _download_idbank_list(update=False, silent=True, insee_date_test=None):

    keys = _get_credentials()

    data = _dwn_idbank_files()

    data = data.iloc[:, 0:3]
    data.columns = ["nomflow", "idbank", "cleFlow"]
    data = data.sort_values("nomflow").reset_index(drop=True)

    return data
