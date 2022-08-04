# -*- coding: utf-8 -*-

import warnings
from pynsee.geodata.GeoFrDataFrame import GeoFrDataFrame
from pynsee.geodata._get_geodata import _get_geodata


def get_geodata(id, update=False, crs="EPSG:3857"):
    """Get geographical data with identifier and from IGN API

    Args:
        id (str): data identifier from get_geodata_list function

        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.

        crs (str, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')

    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = _get_geodata(id=id, update=update, crs=crs)

        df = GeoFrDataFrame(df)

    return df
