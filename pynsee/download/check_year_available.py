import re

from pynsee.download._get_dict_data_source import _get_dict_data_source

def check_year_available(data):
    donnees = data.upper()
    dict_data_source = _get_dict_data_source()
    liste_nom = dict_data_source.keys()
    liste_nom_no_suffix = [re.sub(r'_\d{4}$', '', x) for x in liste_nom]
    res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]

    if bool(res) is False:
        raise ValueError("Data name is mispelled or does not exist")

    liste_possible = [list(liste_nom)[i] for i in res]
    liste_possible = {lname: dict_data_source[lname] for lname in liste_possible}
    return liste_possible