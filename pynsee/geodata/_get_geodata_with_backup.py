from pandas import DataFrame

from ._find_wfs_closest_match import _find_wfs_closest_match
from ._get_geodata import _get_geodata


def _get_geodata_with_backup(string: str) -> DataFrame:

    df = _get_geodata(string)

    if "status" in df.columns:
        if df.loc[0, "status"] == 400:
            str_replacement = _find_wfs_closest_match(string)
            df = _get_geodata(str_replacement)

    return df
