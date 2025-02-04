import logging
import math
import warnings
from typing import Optional

import pandas as pd
from geopandas import GeoDataFrame
from shapely.affinity import translate as trs
from shapely.geometry import Point

from ._make_offshore_points import _make_offshore_points
from ._rescale_geom import _rescale_geom
from ._get_center import _get_center
from ._add_insee_dep import _add_insee_dep


logger = logging.getLogger(__name__)


def translate(
    gdf: GeoDataFrame,
    departement: tuple[str, ...] = ("971", "972", "974", "973", "976"),
    factor: tuple[Optional[float], ...] = (None, None, None, 0.35, None),
    center: tuple[float, float] = (-133583.39, 5971815.98),
    radius: float = 650000,
    angle: float = 1 / 9 * math.pi,
    startAngle: float = math.pi * (1 - 1.5 * 1 / 9),
) -> GeoDataFrame:
    """
    Move overseas departements closer to metropolitan France

    Args:
        departement (tuple, optional): list of departements to be moved, overseas departement list is used by default

        factor (tuple, optional): make departements bigger or smaller, it should correspond to the departement list.
        This parameter is used by shapely.affinity.scale function, please refer to its documentation to choose the value.
        By default, only Guyane's size is reduced. If the value is None, no rescaling is performed.

        center (tuple, optional): center point from which offshore points are computed to move overseas departement
        It should be defined as a (longitude, latitude) point in crs EPSG:3857

        radius (float, optional): radius used with center point to make offshore points, distance in meter

        angle (float, optional): angle used between offshore points, by default it is pi/9

        startAngle (float, optional): start angle defining offshore points, by default it is pi * (1 - 1.5 * 1/9))

    Notes:
        by default translate method focuses on overseas departement, but it can be used to move
        any departement anywhere on the map

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> gdf = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')
        >>> #
        >>> # Move overseas departements closer to metropolitan France
        >>> dfTranslate = gdf.translate()
    """
    init_crs = gdf.crs

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if init_crs != "EPSG:3857":
            logging.warn("Converting GeoDataFrame to EPSG:3857.")
            gdf.to_crs("EPSG:3857")

        if "insee_dep" not in gdf.columns:
            gdf = _add_insee_dep(gdf.copy())

        if "insee_dep" in gdf.columns:
            offshore_points = _make_offshore_points(
                center=Point(center),
                list_ovdep=departement,
                radius=radius,
                angle=angle,
                startAngle=startAngle,
            )

            list_new_dep = []

            for d in range(len(departement)):

                ovdep = gdf[gdf["insee_dep"].isin([departement[d]])]

                if len(ovdep.index) > 0:

                    ovdep = ovdep.reset_index(drop=True)

                    if "insee_dep_geometry" in gdf.columns:
                        geocol = "insee_dep_geometry"
                    else:
                        geocol = "geometry"

                    if factor[d] is not None:
                        ovdep = _rescale_geom(
                            ovdep, factor=factor[d], col=geocol
                        )

                    center_x, center_y = _get_center(ovdep, col=geocol)

                    xoff = offshore_points[d].coords.xy[0][0] - center_x
                    yoff = offshore_points[d].coords.xy[1][0] - center_y

                    ovdep["geometry"] = ovdep["geometry"].apply(
                        lambda x: trs(x, xoff=xoff, yoff=yoff)
                    )

                    list_new_dep += [ovdep]

                else:
                    logger.warning(
                        f"{departement[d]} is missing from insee_dep column !"
                    )

            if len(list_new_dep) > 0:

                ovdepGeo = pd.concat(list_new_dep)

                mainGeo = gdf[~gdf["insee_dep"].isin(departement)].reset_index(
                    drop=True
                )

                finalDF = pd.concat([ovdepGeo, mainGeo]).reset_index(drop=True)

                gdf = finalDF
        else:
            raise ValueError("insee_dep is missing in columns")

        if "insee_dep_geometry" in gdf.columns:
            gdf = gdf.drop(columns="insee_dep_geometry")
            if "insee_dep" in gdf.columns:
                gdf = gdf.drop(columns="insee_dep")

        return gdf
