# -*- coding: utf-8 -*-

import warnings
from pynsee.geodata.GeoDataframe import GeoDataframe
from pynsee.geodata._get_geodata import _get_geodata

def get_geodata(id,
            polygon=None,
            update=False,
            crs='EPSG:3857',
            crsPolygon='EPSG:3857'):
    """Get geographical data with identifier and from IGN API

    Args:
        id (str): _description_
        polygon (Polygon, optional): Polygon used to constraint interested area, its crs must be EPSG:4326. Defaults to None.
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
        df = _get_geodata(id=id, polygon=polygon, update=update, crs=crs, crsPolygon=crsPolygon)

        df = GeoDataframe(df)

    return df

