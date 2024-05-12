import os

import pandas as pd

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata._get_dataset_metadata import _get_dataset_metadata

def _load_dataset_data():
    
    list_dataset = list(get_dataset_list().id.unique())
    list_metadata = []

    if len(list_dataset) > 0:
        for dt in list_dataset:    
            metadata = _get_dataset_metadata(dt, silent=True)
            list_metadata += [metadata]        
    
    if len(list_metadata) > 0:
        return pd.concat(list_metadata)
    else:    
        return None
