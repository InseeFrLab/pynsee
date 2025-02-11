# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import itertools
import re
from unidecode import unidecode

from pynsee.utils.save_df import save_df
from ._clean_data import _clean_data
from ._request_sirene import _request_sirene
from .sirenedataframe import SireneDataFrame

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_search_sirene():
    logger.warning(
        "This function may return personal data, please check and comply with "
        "the legal framework relating to personal data protection !"
    )


@lru_cache(maxsize=None)
def _warning_data_save():
    logger.info(
        "Locally saved data has been used\n"
        "Set update=True to trigger an update"
    )


@save_df(day_lapse_max=30, cls=SireneDataFrame)
def search_sirene(
    variable,
    pattern,
    kind="siret",
    phonetic_search=False,
    and_condition=True,
    upper_case=False,
    decode=False,
    number=1000,
    activity=True,
    legal=False,
    closed=False,
    update=False,
    silent=False,
):
    """Get data about companies from criteria on variables

    Args:
        variable (str or list): name of the variable on which the search is applied.

        pattern (str or list): the pattern or criterium searched

        kind (str, optional): kind of companies : siren or siret. Defaults to "siret"

        phonetic_search (bool, or list of bool, optional): If True phonetic search is triggered on the all variables of the list, if it is a list of True/False, phonetic search is used accordingly on the list of variables

        and_condition (bool, optional): If True, only records meeting all conditions are kept (AND is inserted between the conditions). If False, all records meeting at least one condition are kept (OR is inserted between the conditions).

        number (int, optional): Number of companies searched. Defaults to 1000. If it is above 1000, multiple queries are triggered.

        upper_case (bool, optional): If True, values of argument 'pattern' are converted to upper case and added to the list of searched patterns.

        decode (bool, optional): If True, values of argument 'pattern' are decoded, especially accents are removed and added to the list of searched patterns.

        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.

        legal (bool, optional): If True, legal entities title are added

        closed (bool, optional): If False, closed entities are removed from the data and for each legal entity only the last period for which the data is stable is displayed

        silent (bool, optional): Set to True, to disable messages printed in log info

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
        >>> #
        >>> # Find 1000 companies whose name sounds like Dassault Système or is a big company (GE),
        >>> # search is made as well on patterns whose accents have been removed
        >>> import os
        >>> # environment variable 'pynsee_print_url' force the package to print the request
        >>> os.environ["pynsee_print_url"] = 'True'
        >>> df = search_sirene(variable = ["denominationUniteLegale", 'categorieEntreprise'],
        >>>                 pattern = ['Dassot Système', 'GE'],
        >>>                 and_condition = False,
        >>>                 upper_case = True,
        >>>                 decode = True,
        >>>                 update = True,
        >>>                 phonetic_search  = [True, False],
        >>>                 number = 1000)
    """
    if (not kind == "siret") & (not kind == "siren"):
        raise ValueError("!!! kind should be among : siren, siret !!!")

    if not isinstance(phonetic_search, list):
        if phonetic_search is True:
            phntc_list = [True] * len(variable)
        else:
            phntc_list = [False] * len(variable)
    else:
        check_phonetic_search = all(
            isinstance(x, bool) for x in phonetic_search
        )
        if check_phonetic_search is False:
            raise ValueError(
                "!!! phonetic_search must be True, False or a list of True "
                "and False !!!"
            )

        phntc_list = phonetic_search

    alive = not closed

    if isinstance(variable, str):
        variable = [variable]

    if isinstance(pattern, str):
        pattern = [pattern]

    list_siren_hist_variable = [
        "nomUniteLegale",  #
        "nomUsageUniteLegale",  #
        "denominationUniteLegale",  #
        "denominationUsuelle1UniteLegale",  #
        "denominationUsuelle2UniteLegale",  #
        "denominationUsuelle3UniteLegale",
        "categorieJuridiqueUniteLegale",  #
        "etatAdministratifUniteLegale",  #
        "nicSiegeUniteLegale",  #
        "activitePrincipaleUniteLegale",  #
        "caractereEmployeurUniteLegale",  #
        "economieSocialeSolidaireUniteLegale",  #
        # "nomenclatureActivitePrincipaleUniteLegale",
    ] + ["societeMissionUniteLegale"]

    list_siret_hist_variable = [
        "denominationUsuelleEtablissement",  #
        "enseigne1Etablissement",  #
        "enseigne2Etablissement",  #
        "enseigne3Etablissement",  #
        "activitePrincipaleEtablissement",  #
        "etatAdministratifEtablissement",  #
        "nomenclatureActiviteEtablissement",  #
        "caractereEmployeurEtablissement",  #
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

        # if pattern has several words, split and put mutiple conditions
        # using OR, unless it's a range condition, cf.
        # https://www.sirene.fr/static-resources/htm/sommaire.html
        if not (
            re.match(r"\[\w+\s+TO\s+\w+\]", patt)
            or re.match(r"\{\w+\s+TO\s+\w+\}", patt)
        ):
            patt = re.sub(r"\s+", "|", patt)
        else:
            # only single spaces are accepted in ranges
            patt = re.sub(r"\s+", " ", patt)

        list_patt = patt.split("|")

        if upper_case:
            list_var_patt_maj = [p.upper() for p in list_patt]
            list_patt += list_var_patt_maj

        if decode:
            list_var_decode = [unidecode(p) for p in list_patt]
            list_patt += list_var_decode

        list_patt = list(set(list_patt))

        list_var_patt = []
        for ptt in list_patt:
            if var in list_hist_variable:
                ptt_h = "periode({}{}:{})".format(var, phntc_string, ptt)
            else:
                ptt_h = "{}{}:{}".format(var, phntc_string, ptt)

            list_var_patt += [ptt_h]

        list_var_pattern.append(list_var_patt)

    if and_condition:
        condition = " AND "
    else:
        condition = " OR "

    permutation = list(itertools.product(*list_var_pattern))
    permutation_and = [condition.join(list(x)) for x in permutation]
    permutation_and_parenth = ["(" + x + ")" for x in permutation_and]
    string_query = " OR ".join(permutation_and_parenth)

    query = "?q=" + string_query

    data_final = _request_sirene(query=query, kind=kind, number=number)

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

    return df
