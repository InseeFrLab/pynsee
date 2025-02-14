# -*- coding: utf-8 -*-

from typing import Any, Optional

from geopandas import GeoDataFrame

from .geofrdataframe import GeoFrDataFrame
from ._get_geodata import _get_geodata


def get_geodata(
    dataset_id: str,
    update: bool = False,
    crs: Any = "EPSG:3857",
    constrain_area: Optional[GeoDataFrame] = None,
) -> GeoFrDataFrame:
    """Get geographical data with identifier and from IGN API

    Args:
        id (str): data identifier from get_geodata_list function

        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.

        crs (any valid :class:`~pyproj.crs.CRS` input, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.

        constrain_area (:class:`~geopandas.GeoDataFrame`, optional): GeoDataFrame used to constrain the area of interest. Defaults to None.

    .. versionchanged: 0.2.0

        Changed `polygon` and `crsPolygon` into a `constrain_area` :class:`~geopandas.GeoDataFrame`.

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')

    """
    polygon = None
    crsPolygon = "EPSG:4326"

    if constrain_area is not None:
        if constrain_area.crs.to_string() not in ("EPSG:3857", "EPSG:4326"):
            constrain_area = constrain_area.to_crs("EPSG:4326")

        polygon = constrain_area.union_all()
        crsPolygon = constrain_area.crs.to_string()

    return _get_geodata(
        dataset_id=dataset_id,
        update=update,
        crs=crs,
        ignore_error=False,
        polygon=polygon,
        crs_polygon=crsPolygon,
    )
