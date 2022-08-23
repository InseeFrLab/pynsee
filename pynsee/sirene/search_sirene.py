# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
from functools import lru_cache
import itertools
import pandas as pd
import re

from pynsee.sirene._clean_data import _clean_data
from pynsee.sirene._request_sirene import _request_sirene
from pynsee.sirene.SireneDataFrame import SireneDataFrame
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash


@lru_cache(maxsize=None)
def _warning_search_sirene():
    print(
        "\n!!! This function may return personal data, please check and\n comply with the legal framework relating to personal data protection !!!"
    )


@lru_cache(maxsize=None)
def _warning_data_save():
    print(f"Locally saved data has been used\nSet update=True to trigger an update")


def search_sirene(
    variable,
    pattern,
    kind="siret",
    phonetic_search=False,
    number=1000,
    activity=True,
    legal=False,
    closed=False,
    update=False,
):
    """Get data about companies from criteria on variables

    Args:
        variable (str or list): name of the variable on which the search is applied.

        pattern (str or list): the pattern or criterium searched

        kind (str, optional): kind of companies : siren or siret. Defaults to "siret"

        phonetic_search (bool, or list of bool, optional): If True phonetic search is triggered on the all variables of the list, if it is a list of True/False, phonetic search is used accordingly on the list of variables

        number (int, optional): Number of companies searched. Defaults to 1000. If it is above 1000, multiple queries are triggered.

        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.

        legal (bool, optional): If True, legal entities title are added

        closed (bool, optional): If False, closed entities are removed from the data and for each legal entity only the last period for which the data is stable is displayed.

    Notes:
        This function may return personal data, please check and
        comply with the legal framework relating to personal data protection

    Examples:
        >>> from pynsee.metadata import get_activity_list
        >>> from pynsee.sirene import search_sirene
        >>> from pynsee.sirene import get_dimension_list
        >>> #
        >>> # Get available column names, it is useful to design your query with search_sirene
        >>> sirene_dimension = get_dimension_list()
        >>> #
        >>> # Get activity list (NAF rev 2)
        >>> naf5 = get_activity_list('NAF5')
        >>> #
        >>> # Get a list of hospitals in Paris
        >>> df = search_sirene(variable = ["activitePrincipaleUniteLegale",
        >>>                                "codePostalEtablissement"],
        >>>                    pattern = ["86.10Z", "75*"], kind = "siret")
        >>> #
        >>> # Get a list of companies located in Igny city whose name matches with 'pizza' using a phonetic search
        >>> df = search_sirene(variable = ["libelleCommuneEtablissement",
        >>>                            'denominationUniteLegale'],
        >>>                    pattern = ["igny", 'pizza'],
        >>>                    phonetic_search=True, kind = "siret")
        >>> #
        >>> # Get a list of companies whose name matches with 'SNCF' (French national railway company)
        >>> # and whose legal status is SAS (societe par actions simplifiee)
        >>> df = search_sirene(variable=["denominationUniteLegale",
        >>>                              'categorieJuridiqueUniteLegale'],
        >>>                    pattern=["sncf", '5710'], kind="siren")
        >>> #
        >>> # Get data on Hadrien Leclerc
        >>> df = search_sirene(variable = ['prenom1UniteLegale', 'nomUniteLegale'],
        >>>                           pattern = ['hadrien', 'leclerc'],
        >>>                           phonetic_search = [True, False],
        >>>                           closed=True)
        >>> #
        >>> # Find 2500 tobacco shops
        >>> df = search_sirene(variable = ['denominationUniteLegale'],
        >>>            pattern = ['tabac'],
        >>>            number = 2500,
        >>>            kind = "siret")
    """
    if (not kind == "siret") & (not kind == "siren"):
        raise ValueError("!!! kind should be among : siren, siret !!!")

    if type(phonetic_search) is not list:
        if phonetic_search is True:
            phntc_list = [True] * len(variable)
        else:
            phntc_list = [False] * len(variable)
    else:
        check_phonetic_search = all([(x in [True, False]) for x in phonetic_search])
        if check_phonetic_search is False:
            raise ValueError(
                "!!! phonetic_search must be True, False or a list of True and False !!!"
            )
        else:
            phntc_list = phonetic_search

    if closed is False:
        alive = True
    else:
        alive = False

    if type(variable) == str:
        variable = [variable]

    if type(pattern) == str:
        pattern = [pattern]

    list_siren_hist_variable = [
        "nomUniteLegale",
        "nomUsageUniteLegale",
        "denominationUniteLegale",
        "denominationUsuelle1UniteLegale",
        "denominationUsuelle2UniteLegale",
        "denominationUsuelle3UniteLegale",
        "categorieJuridiqueUniteLegale",
        "etatAdministratifUniteLegale" "nicSiegeUniteLegale",
        "activitePrincipaleUniteLegale",
        "caractereEmployeurUniteLegale",
        "economieSocialeSolidaireUniteLegale",
        "nomenclatureActivitePrincipaleUniteLegale",
    ]

    list_siret_hist_variable = [
        "denominationUsuelleEtablissement",
        "enseigne1Etablissement",
        "enseigne2Etablissement",
        "enseigne3Etablissement",
        "activitePrincipaleEtablissement",
        "etatAdministratifEtablissement",
        "nomenclatureActiviteEtablissement",
        "caractereEmployeurEtablissement",
    ]

    if kind == "siren":
        list_hist_variable = list_siren_hist_variable
    else:
        list_hist_variable = list_siret_hist_variable

    list_var_pattern = []

    for var, patt, phntc in zip(variable, pattern, phntc_list):

        if phntc is False:
            phntc_string = ""
        else:
            phntc_string = ".phonetisation"

        # if pattern has several words, split and put mutiple conditions with OR
        patt = re.sub(r"\s+", "|", patt)
        list_patt = patt.split("|")

        list_var_patt = []
        for ptt in list_patt:
            if var in list_hist_variable:
                list_var_patt.append("periode({}{}:{})".format(var, phntc_string, ptt))
            else:
                list_var_patt.append("{}{}:{}".format(var, phntc_string, ptt))

        list_var_pattern.append(list_var_patt)

    permutation = list(itertools.product(*list_var_pattern))
    permutation_and = [" AND ".join(list(x)) for x in permutation]
    permutation_and_parenth = ["(" + x + ")" for x in permutation_and]
    string_query = " OR ".join(permutation_and_parenth)

    query = "?q=" + string_query
    list_var_string = [str(b) for b in [kind, number]]
    string = "".join(list_var_string)

    filename = _hash(query + string)
    insee_folder = _create_insee_folder()
    file_sirene = insee_folder + "/" + filename

    if (not os.path.exists(file_sirene)) or update:

        data_final = _request_sirene(query=query, kind=kind, number=number)

        data_final.to_pickle(file_sirene)
        print(f"Data saved: {file_sirene}")

    else:
        try:
            data_final = pd.read_pickle(file_sirene)
        except:
            os.remove(file_sirene)

            data_final = search_sirene(
                variable=variable,
                pattern=pattern,
                kind=kind,
                phonetic_search=phonetic_search,
                number=number,
                activity=activity,
                legal=legal,
                closed=closed,
                update=True,
            )

        else:
            _warning_data_save()

    df = _clean_data(
        data_final.copy(),
        kind=kind,
        clean=False,
        activity=activity,
        legal=legal,
        only_alive=alive,
    )

    if df is not None:
        df = df.reset_index(drop=True)

    _warning_search_sirene()

    SireneDF = SireneDataFrame(df)

    return SireneDF
