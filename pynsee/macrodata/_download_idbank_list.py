# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import requests
import zipfile
import pandas as pd
import os
import re
from datetime import date
from datetime import datetime

from pynsee.macrodata._dwn_idbank_files import _dwn_idbank_files

from pynsee.utils._hash import _hash
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._get_temp_dir import _get_temp_dir
from pynsee.utils._get_credentials import _get_credentials


def _download_idbank_list(update=False):

    todays_date = date.today()
    file_to_dwn_default = 'idbank_' + str(todays_date.year) + str(todays_date.month)

    insee_folder = _create_insee_folder()
    file = insee_folder + "/" + _hash(file_to_dwn_default)

    trigger_update = False

    # if the data is not saved locally, or if it is too old (>90 days)
    # then an update is triggered

    if not os.path.exists(file):
        trigger_update = True
    else:
        try:
            # only used for testing purposes
            insee_date_time_now = os.environ['insee_date_test']
            insee_date_time_now = datetime.strptime(
                insee_date_time_now, '%Y-%m-%d %H:%M:%S.%f')
        except:
            insee_date_time_now = datetime.now()

        # file date creation
        file_date_last_modif = datetime.fromtimestamp(os.path.getmtime(file))
        day_lapse = (insee_date_time_now - file_date_last_modif).days

        if day_lapse > 90:
            trigger_update = True

    if update:
        trigger_update = True

    if trigger_update:
        
        # INSEE api credentials are not useful here, but proxy settings stored in pynsee_api_credentials are useful
        keys = _get_credentials()

        data = _dwn_idbank_files()

        data = data.iloc[:, 0:3]
        data.columns = ["nomflow", "idbank", "cleFlow"]
        data = data.sort_values("nomflow").reset_index(drop=True)

        data.to_pickle(file)
     
    else:
        # pickle format depends on python version
        # then read_pickle can fail, if so
        # the file is removed and the function is launched again
        # testing requires multiple python versions
        try:
            data = pd.read_pickle(file)
        except:
            os.remove(file)
            data = _download_idbank_list()

    return data
