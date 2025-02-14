import io
import zipfile
import importlib
import pandas as pd

from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def _get_dataset_list_internal(silent=False):
    """
    silent (bool, optional): Set to True, to disable messages printed in log info
    """

    try:
        pkg_macrodata = importlib.resources.files(__name__)
        zip_file = str(pkg_macrodata) + "/data/dataset_list_internal.zip"
    except Exception:
        import pkg_resources

        zip_file = pkg_resources.resource_stream(
            __name__, "data/dataset_list_internal.zip"
        )

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        dataset_file = io.BytesIO(zip_ref.read("dataset_list_internal.csv"))

    dataset_list = pd.read_csv(
        dataset_file, encoding="utf-8", quotechar='"', sep=",", dtype=str
    )

    col = "Unnamed: 0"
    if col in dataset_list.columns:
        dataset_list = dataset_list.drop(columns={col})

    return dataset_list
