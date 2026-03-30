import difflib

from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.utils.HiddenPrints import HiddenPrints

string = "ADMINEXPRESS-COG.LATEST:departement"


def _find_wfs_closest_match(string: str = string, limit: int = 1) -> list:
    """
    Find the X closest matches among available WFS datasets.

    Parameters
    ----------
    string : str, optional
        Dataset identifier to match. The default is ADMINEXPRESS-COG.LATEST:departement.
    limit : int, optional
        Maximum number of datasets to retrieve. The default is 1.

    Returns
    -------
    list
        List of potential matches.

    """

    with HiddenPrints():
        wfs = get_geodata_list()

    list_sugg = list(wfs.Identifier.unique())
    suggestions = difflib.get_close_matches(string, list_sugg)
    return suggestions[:limit]
