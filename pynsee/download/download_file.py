from pynsee.download._download_store_file import _download_store_file
from pynsee.download._load_data_from_schema import _load_data_from_schema


def download_file(id, variables=None, update=False):
    """User level function to download files from insee.fr

    Args:
        id (str): file id, check get_file_list to have a full list of available files

        variables (list): a list of variables to load from the data file, use get_column_metadata function to have the full list

        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False.


    Returns:
        Returns the request dataframe as a pandas object

    Examples:
        >>> from pynsee.download import download_file
        >>> df = download_file("AIRE_URBAINE")

    """

    try:

        dwn = _download_store_file(id, update=update)
        df = _load_data_from_schema(dwn, variables=variables)

        return df
    except:
        raise ValueError("Download failed")
