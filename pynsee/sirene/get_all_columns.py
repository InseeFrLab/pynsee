# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.sirene import search_sirene


def get_all_columns(kind='siret'):
    """Get a list of all columns useful to make queries with search_sirene

    Args:
        kind (str, optional): Choose between siret and siren. Defaults to 'siret'.

    Examples:
        >>> from pynsee.sirene import get_all_columns
        >>> sirene_columns = get_all_columns()
    """

    if kind == 'siret':
        df = search_sirene(variable=['sigleUniteLegale'],
                           pattern=['INSEE'],
                           kind='siret',
                           number=1, clean=False)
        col = ['siret_columns', 'example']

    else:
        df = search_sirene(variable=['sigleUniteLegale'],
                           pattern=['INSEE'], kind='siren',
                           number=1, clean=False)
        col = ['siren_columns', 'example']

    df = df.T
    df = df.reset_index(drop=False)
    df.columns = col
    name_first_col = df.columns[0]

    list_added_col = ['categorieJuridiqueUniteLegale',
                      'activitePrincipaleUniteLegale',
                      'activitePrincipaleEtablissement',
                      'typeVoieEtablissement']
    list_added_col = [c + 'Libelle' for c in list_added_col]
    list_added_col = list_added_col + \
        ['effectifsMinEtablissement', 'effectifsMaxEtablissement']

    string_col_remove = ['^' + c + '$' for c in list_added_col]
    string_col_remove = '|'.join(string_col_remove)

    df = df[~(df[name_first_col].str.contains(string_col_remove))]
    df = df.reset_index(drop=True)

    return(df)
