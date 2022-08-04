import zipfile
import pkg_resources
import pandas as pd

from pynsee.utils._create_insee_folder import _create_insee_folder


def _get_dataset_list_internal():

    zip_file = pkg_resources.resource_stream(__name__, "data/dataset_list_internal.zip")

    insee_folder = _create_insee_folder()
    dataset_file = insee_folder + "/" + "dataset_list_internal.csv"

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(insee_folder)

    dataset_list = pd.read_csv(
        dataset_file, encoding="utf-8", quotechar='"', sep=",", dtype=str
    )

    col = "Unnamed: 0"
    if col in dataset_list.columns:
        dataset_list = dataset_list.drop(columns={col})

    return dataset_list
