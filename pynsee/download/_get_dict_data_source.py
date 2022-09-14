import requests
import re
import os
from functools import lru_cache
import urllib3

from pynsee.download._get_file_list_internal import _get_file_list_internal


@lru_cache(maxsize=None)
def _get_dict_data_source():

    try:
        URL_DATA_LIST = os.environ["pynsee_file_list"]
    except:
        URL_DATA_LIST = (
            "https://raw.githubusercontent.com/"
            + "InseeFrLab/DoReMIFaSol/master/data-raw/liste_donnees.json"
        )
    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["https_proxy"]}
    except:
        proxies = {"http": "", "https": ""}
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        jsonfile = requests.get(URL_DATA_LIST, proxies=proxies, verify=False).json()
    except:
        jsonfile = _get_file_list_internal()

        print("\n!!! Package's internal data has been used !!!\n")
        print("!!! File list download failed !!!")
        print("!!! Please contact the package maintainer if this error persists !!!\n")

    # HACK BECAUSE OF DUPLICATED ENTRIES -------------------------------

    potential_keys = [items["nom"] for items in jsonfile]
    list_duplicated_sources = list(
        set([x for x in potential_keys if potential_keys.count(x) > 1])
    )

    dict_data_source = {
        _create_key(item, list_duplicated_sources): item for item in jsonfile
    }

    return dict_data_source


def _create_key(item, duplicate_sources):
    """
    Transform JSON into Python dict

    Args:
        item: Item in JSON source
        duplicate_sources: List of duplicate sources in JSON

    Returns: Initial dict with modified keys to avoid duplicated entries

    """
    if item["nom"] not in duplicate_sources:
        return item["nom"]
    dateref = item["date_ref"]
    year = re.search(r"\d{4}", dateref).group(0)
    return f"{item['nom']}_{year}"
