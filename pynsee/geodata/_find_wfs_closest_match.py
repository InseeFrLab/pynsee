import os
import sys
import difflib

from pynsee.geodata._get_geodata import _get_geodata
from pynsee.geodata.get_geodata_list import get_geodata_list

string = "ADMINEXPRESS-COG.LATEST:departement"

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def _find_wfs_closest_match(string=string):
    with HiddenPrints():
        wfs = get_geodata_list()    

    list_sugg = list(wfs.Identifier.unique()) 
    suggestions = difflib.get_close_matches(
                string, list_sugg
            )
    return suggestions[0]
