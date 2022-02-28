# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache

from pynsee.utils._paste import _paste
from pynsee.sirene._clean_data import _clean_data
from pynsee.sirene._request_sirene import _request_sirene
from pynsee.sirene.SireneDataframe import SireneDataframe

@lru_cache(maxsize=None)
def _warning_search_sirene():
    print("\n!!! This function may return personal data, please check and\n comply with the legal framework relating to personal data protection !!!")


def search_sirene(variable,
                  pattern,
                  kind="siret",
                  phonetic_firstvar=False,
                  number=1000,
                  clean=True,
                  activity=True,
                  legal=True,
                  only_alive=True,
                  query_limit=20):
    """Get data about companies from criteria on variables

    Args:
        variable (str or list): name of the variable on which the search is applied.

        pattern (str or list): the pattern or criterium searched

        kind (str, optional): kind of companies : siren or siret. Defaults to "siren".

        phonetic_firstvar (bool, optional): If True phonetic search is triggered on the
        first variable of the list, if False the exact string is searched. Defaults to True.

        number (int, optional): Number of companies searched. Defaults to 1000.
        If it is above 1000, multiple queries are triggered.

        clean (bool, optional): If True, empty columns are deleted. Defaults to True.

        activity (bool, optional): If True, activty title is added based on NAF/NACE. Defaults to True.

        legal (bool, optional): If True, legal entities title are added

        only_alive (bool, optional): If True, closed entities are removed from the data and
        for each legal entity only the last period for which the data is stable is displayed

        query_limit(numeric, optional): maximun number of queries made
         by the function in a row, by default it is 20

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
        >>>                    phonetic_firstvar=True, kind = "siret")
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
        >>>                           kind = 'siret', only_alive = False)
        >>> #
        >>> # Find 2500 tobacco shops
        >>> df = search_sirene(variable = ['denominationUniteLegale'],
        >>>            pattern = ['tabac'],
        >>>            number = 2500,
        >>>            kind = "siret")
    """
    if (not kind == 'siret') & (not kind == 'siren'):
        raise ValueError('!!! kind should be among : siren, siret !!!')

    if type(variable) == str:
        variable = [variable]

    if type(pattern) == str:
        pattern = [pattern]

    list_siren_hist_variable = [
        'nomUniteLegale',
        'nomUsageUniteLegale',
        'denominationUniteLegale',
        'denominationUsuelle1UniteLegale',
        'denominationUsuelle2UniteLegale',
        'denominationUsuelle3UniteLegale',
        'categorieJuridiqueUniteLegale',
        'etatAdministratifUniteLegale'
        'nicSiegeUniteLegale',
        'activitePrincipaleUniteLegale',
        'caractereEmployeurUniteLegale',
        'economieSocialeSolidaireUniteLegale',
        'nomenclatureActivitePrincipaleUniteLegale'
    ]

    list_siret_hist_variable = ['denominationUsuelleEtablissement',
                                'enseigne1Etablissement',
                                'enseigne2Etablissement',
                                'enseigne3Etablissement',
                                'activitePrincipaleEtablissement',
                                'etatAdministratifEtablissement',
                                'nomenclatureActiviteEtablissement',
                                'caractereEmployeurEtablissement']

    if kind == 'siren':
        list_hist_variable = list_siren_hist_variable
    else:
        list_hist_variable = list_siret_hist_variable

    list_var_pattern = []

    for var, patt in zip(variable, pattern):

        phntc = ""
        if var == variable[0]:
            if phonetic_firstvar:
                phntc = ".phonetisation"

        # if pattern has several words, split and put mutiple conditions with OR
        list_patt = patt.split(' ')

        list_var_patt = []
        for ptt in list_patt:
            if var in list_hist_variable:
                list_var_patt.append(
                    "periode({}{}:{})".format(var, phntc, ptt))
            else:
                list_var_patt.append("{}{}:{}".format(var, phntc, ptt))

        list_var_pattern.append(_paste(list_var_patt, collapse=" OR "))

    query = "?q=" + _paste(list_var_pattern, collapse=" AND ")

    data_final = _request_sirene(query=query, kind=kind,
                                 number=number, query_limit=query_limit)

    df = _clean_data(data_final, kind=kind,
                     clean=clean, activity=activity,
                     legal=legal, only_alive=only_alive)

    if df is not None:
        df = df.reset_index(drop=True)

    _warning_search_sirene()

    SireneDF = SireneDataframe(df)

    return(SireneDF)
