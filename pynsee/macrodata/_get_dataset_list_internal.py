import zipfile
import pkg_resources
import pandas as pd
import os

from pynsee.utils.save_df import save_df
from pynsee.utils._get_temp_dir import _get_temp_dir

@save_df(day_lapse_max=90)
def _get_dataset_list_internal():

    zip_file = pkg_resources.resource_stream(__name__, "data/dataset_list_internal.zip")

    temp_folder = _get_temp_dir()
    dataset_file = os.path.join(temp_folder, "dataset_list_internal.csv")

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    dataset_list = pd.read_csv(
        dataset_file, encoding="utf-8", quotechar='"', sep=",", dtype=str
    )

    col = "Unnamed: 0"
    if col in dataset_list.columns:
        dataset_list = dataset_list.drop(columns={col})

    return dataset_list
