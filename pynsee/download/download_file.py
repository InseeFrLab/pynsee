import tempfile

from pandas import DataFrame

from pynsee.download._download_store_file import _download_store_file
from pynsee.download._load_data_from_schema import _load_data_from_schema

from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def download_file(id, variables=None, update=False, silent=False) -> DataFrame:
    """
    User level function to download files from insee.fr

    Note: in the case of vintaged ids (ie. TAG_COM_2025), it should be safe to
    use a _LATEST tag instead if you just want the latest available dataset
    (ie TAG_COM_LATEST). In case of side-effects, pay attention to the log
    entries and revert to the vintaged id.

    Args:
        id (str): file id, check get_file_list to have a full list of available files

        variables (list): a list of variables to load from the data file, use
          get_column_metadata function to have the full list

        update (bool, optional): Trigger an update, otherwise locally saved data is
          used. Defaults to False.

        silent (bool, optional): Set to True, to disable messages printed in log info

    Returns:
        Returns the request dataframe as a pandas object

    Examples:
        >>> from pynsee.download import download_file
        >>> df = download_file("TAG_COM_LATEST")

    """

    with tempfile.TemporaryDirectory() as tmpdir:

        dwn = _download_store_file(tmpdir, id)
        df = _load_data_from_schema(dwn, variables=variables)

    return df
