from pynsee.download.download_store_file import download_store_file
from pynsee.download._load_data_from_schema import _load_data_from_schema

def load_data(data, date, teldir=None, variables_names=None):
    """
    User level function to download datasets from insee.fr

    Args:
        data: Dataset name
        date: Year. Can be an integer. Can also be 'recent' or 'latest'
                 to get latest dataset
        teldir: Where output should be written
        variables_names: Subset of variable names to use.
                 If None (default), ignored

    Returns:
        Returns the request dataframe as a pandas object

    """
    try:
        return _load_data_from_schema(
            download_store_file(data=data, date=date, teldir=teldir),
            variables_names
        )
    except:
        raise ValueError("Download failed")