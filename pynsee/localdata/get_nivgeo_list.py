# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

from pynsee.localdata._warning_local_data import _warning_local_data

@lru_cache(maxsize=None)
def _warning_local_data():
    print("!!! This function renders only package's internal data,\nit might not be the most up-to-date\nHave a look at api.insee.fr !!!")


def get_nivgeo_list():
    """Get a list of geographic levels

    Examples
        >>> from pynsee.localdata import get_nivgeo_list
        >>> nivgeo_list = get_nivgeo_list()
    """
    _warning_local_data()

    dict_ng = {
        'NIVGEO': ['COM',
                   'DEP',
                   'REG',
                   'METRODOM',
                   'FE',
                   'ARR',
                   'EPCI',
                   'AAV2020',
                   'UU2020',
                   'ZE2020',
                   'AU2010',
                   'UU2010',
                   'ZE2010'],
        'NIVGEO_label_fr': ['communes et arrondissements municipaux',
                            'départements',
                            'régions',
                            'France métropolitaine',
                            'France',
                            'arrondissements',
                            'intercommunalités',
                            "aires d'attraction des villes 2020",
                            'unités urbaines 2020',
                            "zones d'emploi 2020",
                            "aires urbaines 2010",
                            'unités urbaines 2010',
                            "zones d'emploi 2010"],
        'NIVGEO_label_en': ['municipalities and municipal districts',
                            'departments',
                            'regions',
                            'metropolitan France',
                            'France',
                            'districts',
                            'intermunicipal authorities',
                            'functional areas 2020',
                            'urban unit 2020',
                            'employment zone 2020',
                            'urban area 2010',
                            'urban unit 2010',
                            'employment zone 2010']
    }

    nivgeo = pd.DataFrame(dict_ng)
    return(nivgeo)
