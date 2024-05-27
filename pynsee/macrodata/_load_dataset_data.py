import os
import pandas as pd
from tqdm import trange

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata._get_dataset_metadata import _get_dataset_metadata
from pynsee.utils.save_df import save_df

@save_df(day_lapse_max=90)
def _load_dataset_data(update=False, silent=True):
    
    list_dataset = list(get_dataset_list(silent=True).id.unique())
    list_metadata = []

    for dt in trange(len(list_dataset), desc='Metadata download'):    
        dataset = list_dataset[dt]
        metadata = _get_dataset_metadata(dataset, silent=True)
        list_metadata += [metadata]        
    
    return pd.concat(list_metadata)
