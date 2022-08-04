import pandas as pd
from functools import lru_cache

from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.utils._move_col_after import _move_col_before


@lru_cache(maxsize=None)
def get_file_list():
    """Download a list of files available on insee.fr

    Returns:
        Returns the requested dataframe as a pandas object

    Notes:
        pynsee.download's metadata rely on volunteering contributors and their manual updates.
        get_file_list does not provide data from official Insee's metadata API.
        Consequently, please report any issue

    Examples:
        >>> from pynsee.download import get_file_list
        >>> insee_file_list = get_file_list()

    """

    df = pd.DataFrame(_get_dict_data_source()).T

    df["id"] = df.index
    df = df.reset_index(drop=True)
    df = _move_col_before(df, "id", "nom")

    df.columns = [
        "id",
        "name",
        "label",
        "collection",
        "link",
        "type",
        "zip",
        "big_zip",
        "data_file",
        "tab",
        "first_row",
        "api_rest",
        "md5",
        "size",
        "label_col",
        "date_ref",
        "meta_file",
        "separator",
        "type_col",
        "long_col",
        "val_col",
        "encoding",
        "last_row",
        "missing_value",
    ]

    df = df[~df.link.str.contains("https://api.insee.fr")]

    warning_metadata_download()

    return df


@lru_cache(maxsize=None)
def warning_metadata_download():

    print(
        "pynsee.download's metadata rely on volunteering contributors and their manual updates"
    )
    print(
        "get_file_list does not provide data from official Insee's metadata API\nConsequently, please report any issue"
    )
