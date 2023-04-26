import os
import sys
import difflib

from pynsee.geodata._get_geodata import _get_geodata
from pynsee.geodata.get_geodata_list import get_geodata_list

string = "ADMINEXPRESS-COG.LATEST:departement"

def _find_wfs_closest_match(string=string):
    sys.stdout = open(os.devnull, 'w')
    wfs = get_geodata_list()
    sys.stdout = sys.__stdout__
    

    list_sugg = list(wfs.Identifier.unique()) 
    suggestions = difflib.get_close_matches(
                string, list_sugg
            )
    return suggestions[0]
