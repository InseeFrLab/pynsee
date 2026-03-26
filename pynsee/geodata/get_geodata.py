# -*- coding: utf-8 -*-

import logging
from typing import Any, Optional

from geopandas import GeoDataFrame

from .geofrdataframe import GeoFrDataFrame
from ._get_geodata import _get_geodata
from ._find_wfs_closest_match import _find_wfs_closest_match
from .get_geodata_list import get_geodata_list

logger = logging.getLogger(__name__)


def get_geodata(
    dataset_id: str,
    update: bool = False,
    crs: Any = "EPSG:3857",
    constrain_area: Optional[GeoDataFrame] = None,
    silent: bool = False,
) -> GeoFrDataFrame:
    """
    Get geographical data with identifier and from IGN API

    Args:
        id (str): data identifier from get_geodata_list function

        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.

        crs (any valid :class:`~pyproj.crs.CRS` input, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.

        constrain_area (:class:`~geopandas.GeoDataFrame`, optional): GeoDataFrame used to constrain the area of interest. Defaults to None.

        silence (bool, optional): whether to print warnings or not. Defaults to False.

    .. versionchanged: 0.2.0

        Changed `polygon` and `crsPolygon` into a `constrain_area` :class:`~geopandas.GeoDataFrame`.

    .. versionchanged: 0.2.5
        Check if a dataset is discovered in the available datasets before querying the server.
        Querying a unavailable dataset now triggers a ValueError.

        Added silent parameter.




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
    crs_polygon = "EPSG:4326"

    # check if dataset is available to ensure faster failure and helpful hints
    dsets = get_geodata_list()
    if dataset_id not in set(dsets.Identifier):
        closests = _find_wfs_closest_match(dataset_id, limit=5)
        closests = ", ".join([f"'{x}'" for x in closests])
        msg = (
            "Dataset %s wasn't found. You manually check available "
            "datasets using\n"
            "`from pynsee import get_geodata_list;get_geodata_list()`\n"
        )
        logger.error(msg, dataset_id)
        logger.warning("Closests datasets are %s", closests)

        raise ValueError(
            f"{dataset_id} was not found, did you meant any of {closests} ?"
        )

    if constrain_area is not None:
        if constrain_area.crs.to_string() not in ("EPSG:3857", "EPSG:4326"):
            constrain_area = constrain_area.to_crs("EPSG:4326")

        polygon = constrain_area.union_all()
        crs_polygon = constrain_area.crs.to_string()

    return _get_geodata(
        dataset_id=dataset_id,
        update=update,
        crs=crs,
        ignore_error=False,
        polygon=polygon,
        crs_polygon=crs_polygon,
        silent=silent,
    )
