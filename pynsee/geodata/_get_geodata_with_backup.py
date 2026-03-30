import logging

from ._find_wfs_closest_match import _find_wfs_closest_match
from .get_geodata_list import get_geodata_list
from ._get_geodata import _get_geodata
from .geofrdataframe import GeoFrDataFrame

logger = logging.getLogger(__name__)


def _get_geodata_with_backup(string: str) -> GeoFrDataFrame:

    # check if dataset is available to ensure faster backup
    dsets = get_geodata_list()
    if string not in set(dsets.Identifier):
        str_replacement = _find_wfs_closest_match(string)[0]
        logger.warning(
            "%s not found, switching to %s instead", string, str_replacement
        )
        string = str_replacement

    df = _get_geodata(string)

    return df
