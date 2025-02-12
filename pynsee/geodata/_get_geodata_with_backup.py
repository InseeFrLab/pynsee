from requests import RequestException

from ._find_wfs_closest_match import _find_wfs_closest_match
from ._get_geodata import _get_geodata
from .geofrdataframe import GeoFrDataFrame


def _get_geodata_with_backup(string: str) -> GeoFrDataFrame:
    try:
        df = _get_geodata(string, ignore_error=False)
    except RequestException as e:
        res = e.response

        if hasattr(res, "status_code") and res.status_code == 400:
            str_replacement = _find_wfs_closest_match(string)
            df = _get_geodata(str_replacement)
        else:
            raise e

    return df
