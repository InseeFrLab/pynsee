import os
from functools import lru_cache

from pynsee.download._download_store_file import _download_store_file
from pynsee.download._load_data_from_schema import _load_data_from_schema
from pynsee.download._add_metadata import _add_metadata

def download_file(id, metadata=False, update=False):
    """
    User level function to download files from insee.fr

    Args:
        id (str): file id, check get_file_list to have a full list of available files
        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False.

    Returns:
        Returns the request dataframe as a pandas object

    """
    
    try:
        df = _load_data_from_schema(
                _download_store_file(id, update=update)
            )
        
        if metadata is True:
            #try:
                df = _add_metadata(id, df)
            #except:
            #    pass
        else:
            warning_metadata()
            
        return df
    except:
        raise ValueError("Download failed")
        

@lru_cache(maxsize=None)
def warning_metadata():
    
    print("Set metadata=True, to add column-specific metadata to the output")