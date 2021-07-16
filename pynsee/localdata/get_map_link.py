# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
import zipfile
import pkg_resources
from functools import lru_cache

from pynsee.localdata import get_map_list
from pynsee.utils._create_insee_folder import _create_insee_folder


@lru_cache(maxsize=None)
def _warning_map(geo):
    if geo == 'arr':
        msg1 = '!!! Geographic data made on arrondissements municipaux in 2020 come from opendatasoft\n'
        msg2 = 'https://public.opendatasoft.com/explore/dataset/arrondissements-millesimes0/information/ !!!'
    else:
        msg1 = '!!! Geographic data come from https://france-geojson.gregoiredavid.fr/,\n'
        msg2 = 'It has been made in 2018 from INSEE and IGN data !!!'

    print('{}{}'.format(msg1, msg2))


def get_map_link(geo):
    """Get the link of the geojson map file

    Args:
        geo (str): French administrative area (see get_map_list)

    Raises:
        ValueError: an error is raised if geo is not in the list from get_map_list()

    Notes:
        All data come from https://france-geojson.gregoiredavid.fr/, made from INSEE and IGN data in 2018.

        Only arrondissements municipaux data come from https://public.opendatasoft.com/explore/dataset/arrondissements-millesimes0/information/ in 2020.


    Examples:
        >>> from pynsee.localdata import get_map_link
        >>> map_departement_link = get_map_link('departements')
    """

    if geo == 'arrondissements-municipaux':
        _warning_map('arr')
    else:
        _warning_map('other')

    insee_folder = _create_insee_folder()

    insee_folder_map = insee_folder + '/' + 'maps'
    if not os.path.exists(insee_folder_map):
        os.mkdir(insee_folder_map)

    maps_list = get_map_list()

    if geo in list(maps_list['name_fr']):

        geo_file = insee_folder_map + '/' + geo + '.geojson'
        if os.path.exists(geo_file):
            return(geo_file)
        else:
            # unzip files stored in package
            zip_file = pkg_resources.resource_stream(__name__, 'data/maps.zip')

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(insee_folder)

            if os.path.exists(geo_file):
                return(geo_file)
            else:
                raise ValueError('Package error : %s is missing' % geo_file)
    else:
        raise ValueError(
            '%s is not in the list coming from get_map_list' % geo)
