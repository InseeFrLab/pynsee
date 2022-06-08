import re
import difflib

from pynsee.download._check_year_available import _check_year_available
from pynsee.download._get_dict_data_source import _get_dict_data_source

def _info_data(data: str, date=None):
    """Get some info regarding datasets available

    Arguments:
        data {str} -- Dataset name

    Keyword Arguments:
        date -- Desired year for the dataset (default: {None})


    Returns:
        For instance, looks for closed match in the
         keyword given to download_store_file
    """

    if date == "latest":
        date = "dernier"

    donnees = data.upper()
    liste_nom = _get_dict_data_source().keys()
    liste_nom_no_suffix = [re.sub(r'_\d{4}$', '', x) for x in liste_nom]
    res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]

    if not len(res):
        liste_nom_no_suffix_cleaned = list(set(liste_nom_no_suffix))
        suggestions = difflib.get_close_matches(
            donnees,
            liste_nom_no_suffix_cleaned
            )

        if len(suggestions) == 0:
            error_message = "No data found. Did you mispell ?"
        else:
            error_message = f"Data name is mispelled, \
                potential values are: {suggestions}"

        raise ValueError(error_message)

    # 2 - gestion millésimes

    possible = _check_year_available(donnees)

    if (len(possible) > 1) & (date is None):
        raise ValueError("Several versions of this dataset exist, please specify a year")

    if date == "dernier":
        latest = sorted(possible.keys(), key=lambda x: x.lower(), reverse=True)[0]
        possible = possible[latest]
    elif date is not None:
        possible = possible[f"{donnees}_{str(date)}"]

    return possible