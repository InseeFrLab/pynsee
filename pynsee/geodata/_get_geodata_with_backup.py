
from pynsee.geodata._find_wfs_closest_match import _find_wfs_closest_match
from pynsee.geodata. _get_geodata import  _get_geodata

def _get_geodata_with_backup(string):
    
    df = _get_geodata(string)
    if len(df.index) == 1:
        if 'status' in df.columns:
            if df["status"][0] == 400:
                str_replacement = _find_wfs_closest_match(string)
                df = _get_geodata(str_replacement)
    return df
                
    