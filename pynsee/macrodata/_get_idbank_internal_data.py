# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import zipfile
import pkg_resources
import pandas as pd
import os

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def _get_idbank_internal_data(update=False):

    insee_folder = _create_insee_folder()

    data_file = insee_folder + '/' + 'idbank_list_internal.csv'
    data_final_file = insee_folder + '/' + _hash('idbank_list_internal_final') + ".json"
    zip_file = pkg_resources.resource_stream(
        __name__, 'data/idbank_list_internal.zip')

    if (not os.path.exists(data_final_file)) | update:

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)

        idbank_list = pd.read_csv(data_file, encoding='utf-8',
                                  quotechar='"', sep=',', dtype=str)

        col = 'Unnamed: 0'
        if col in idbank_list.columns:
            idbank_list = idbank_list.drop(columns={col})

        os.remove(data_file)
        idbank_list.to_json(data_final_file)
    else:
        idbank_list = pd.read_json(data_final_file, dtype=False)
        
    return idbank_list
