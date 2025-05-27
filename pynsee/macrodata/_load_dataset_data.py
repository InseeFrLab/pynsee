import pandas as pd
from tqdm import trange

from ..utils.save_df import save_df
from .get_dataset_list import get_dataset_list
from ._get_metadata import _get_dataset_metadata


@save_df(day_lapse_max=90)
def _load_dataset_data(datasets=None, update=False, silent=False):

    list_dataset = list(get_dataset_list(silent=silent).id.unique())

    if datasets is not None:
        list_dataset = [d for d in list_dataset if d in datasets]

    list_metadata = []

    for dt in trange(len(list_dataset), desc="Metadata download"):
        dataset = list_dataset[dt]
        metadata = _get_dataset_metadata(dataset, silent=silent)
        list_metadata += [metadata]

    return pd.concat(list_metadata)
