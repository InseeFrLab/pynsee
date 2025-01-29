import difflib

from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.utils.HiddenPrints import HiddenPrints

string = "ADMINEXPRESS-COG.LATEST:departement"


def _find_wfs_closest_match(string=string):
    with HiddenPrints():
        wfs = get_geodata_list()

    list_sugg = list(wfs.Identifier.unique())
    suggestions = difflib.get_close_matches(string, list_sugg)
    return suggestions[0]
