import re
import os
from functools import lru_cache

from pynsee.download._get_file_list_internal import _get_file_list_internal
from pynsee.utils.requests_session import PynseeAPISession

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_dict_data_source():
    try:
        URL_DATA_LIST = os.environ["pynsee_file_list"]
    except KeyError:
        URL_MELODI = "https://minio.lab.sspcloud.fr/pierrelamarche/melodi/liste_donnees.json"
        URL_DOREMIFASOL = "https://raw.githubusercontent.com/InseeFrLab/DoReMIFaSol/master/data-raw/liste_donnees.json"  # inherited from previous pynsee version
        URL_DATA_LIST = [URL_MELODI] + [URL_DOREMIFASOL]

    with PynseeAPISession() as session:
        if isinstance(URL_DATA_LIST, list):
            try:
                jsonfile1 = session.get(URL_MELODI, verify=False).json()
                jsonfile2 = session.get(URL_DOREMIFASOL, verify=False).json()
                jsonfile = jsonfile1 + jsonfile2
            except Exception:
                logger.error("Error when reading sources catalog")
        else:
            try:
                jsonfile = [session.get(URL_DATA_LIST, verify=False).json()]
            except Exception:
                jsonfile = _get_file_list_internal()

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
