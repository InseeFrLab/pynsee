# -*- coding: utf-8 -*-

import warnings
from .GeoFrDataFrame import GeoFrDataFrame
from ._get_geodata import _get_geodata


def get_geodata(
    dataset_id: str, update: bool = False, crs: str = "EPSG:3857"
) -> GeoFrDataFrame:
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

        gdf = _get_geodata(dataset_id=dataset_id, update=update, crs=crs)

        if not isinstance(gdf, GeoFrDataFrame):
            message = (
                f"Request failed: {gdf.loc[0, 'status']}, "
                f"{gdf.loc[0, 'comment']}."
            )

            raise RuntimeError(message)

    return gdf
