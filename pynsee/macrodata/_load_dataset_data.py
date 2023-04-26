import os
import pandas as pd

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from pynsee.macrodata.get_dataset_list import get_dataset_list

def _del_dataset_files():
    list_dataset_files = _get_dataset_files()
    if len(list_dataset_files) > 0:
        for f in list_dataset_files:
            os.remove(f)

def _get_dataset_files():
    list_dataset = list(get_dataset_list().id.unique())
    insee_folder = _create_insee_folder()
    file_dataset_metadata_list = [insee_folder + "/" + _hash("idbank_list" + dt) for dt in list_dataset] 
    file_dataset_metadata_list_exist = [f for f in file_dataset_metadata_list if os.path.exists(f)]
    return file_dataset_metadata_list_exist

def _load_dataset_data():
    list_dataset_files = _get_dataset_files()
    if len(list_dataset_files) > 0:
        return pd.concat([pd.read_pickle(f) for f in list_dataset_files])
    else:
        return None

