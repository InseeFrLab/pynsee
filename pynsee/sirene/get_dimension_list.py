# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.sirene import search_sirene


def get_dimension_list(kind='siret'):
    """Get a list of all columns useful to make queries with search_sirene

    Args:
        kind (str, optional): Choose between siret and siren. Defaults to 'siret'.

    Examples:
        >>> from pynsee.sirene import get_dimension_list
        >>> sirene_dimension = get_dimension_list()
    """

    if kind not in ['siret','siren']:
        raise ValueError("kind must be siret (default) or siren")

    if kind == 'siret':
        df = search_sirene(variable=['sigleUniteLegale'],
                           pattern=['INSEE'],
                           only_alive=False,
                           kind='siret',
                           number=1, clean=False)
        col_to_keep = 0
    else:
        df = search_sirene(variable=['sigleUniteLegale'],
                           pattern=['INSEE'], kind='siren',
                           only_alive=False,
                           number=1, clean=False)
        col_to_keep = 1

    df = df.T
    df = df.reset_index(drop=False)
    df = df.loc[:,["index",col_to_keep]]
    df.columns = ['siret_columns', 'example']
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
