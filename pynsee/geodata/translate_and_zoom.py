import logging
import math
from typing import Optional

import pandas as pd
from geopandas import GeoDataFrame
from shapely.affinity import rotate
from shapely.geometry import Point, LineString

from ._make_offshore_points import _make_offshore_points
from ._rescale_geom import _rescale_geom
from ._get_center import _get_center
from ._add_insee_dep import _add_insee_dep


logger = logging.getLogger(__name__)


def transform_overseas(
    gdf: GeoDataFrame,
    departement: tuple[str, ...] = ("971", "972", "974", "973", "976", "NR"),
    factor: tuple[Optional[float], ...] = (None, None, None, 0.35, None, None),
    center: tuple[float, float] = (-133583.39, 5971815.98),
    radius: float = 650000,
    angle: float = 1 / 9 * math.pi,
    startAngle: float = math.pi * (1 - 2 * 1 / 9),
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

    if init_crs != "EPSG:3857":
        logging.warning("Converting GeoDataFrame to EPSG:3857.")
        gdf = gdf.to_crs("EPSG:3857")

    geocol = "insee_dep_geometry"

    if "cleabs" in gdf and gdf["cleabs"].str.match("DEPARTEM").all():
        # this is already the departments, work on geometry
        geocol = gdf.geometry.name
        gdf["code_insee_du_departement"] = gdf["code_insee"]
        gdf["insee_dep_geometry"] = gdf["geometry"]
    else:
        gdf = _add_insee_dep(gdf.copy()).reset_index(drop=True)

    offshore_points = _make_offshore_points(
        center=Point(center),
        list_ovdep=departement,
        radius=radius,
        angle=angle,
        startAngle=startAngle,
    )

    # keep only specific departements
    list_new_dep = [gdf.loc[~gdf.code_insee_du_departement.isin(departement)]]

    for i, d in enumerate(departement):
        ovdep = gdf.loc[gdf.code_insee_du_departement.values == d].reset_index(
            drop=True
        )

        if ovdep.empty:
            logger.warning(
                "%s is missing from code_insee_du_departement column !", d
            )
        else:
            # get the center of the department to rescale the geometry
            # properly
            center = _get_center(ovdep, geocol=geocol)

            if factor[i] is not None:
                _rescale_geom(ovdep, factor=factor[i], center=center)

            center_x, center_y = center

            xoff = offshore_points[i].coords.xy[0][0] - center_x
            yoff = offshore_points[i].coords.xy[1][0] - center_y

            ovdep.loc[:, ovdep.geometry.name] = ovdep.geometry.translate(
                xoff=xoff, yoff=yoff
            )

            list_new_dep.append(ovdep)

    gdf = pd.concat(list_new_dep, ignore_index=True)

    return gdf.drop(columns=["insee_dep_geometry"], errors="ignore")


def zoom(
    gdf: GeoDataFrame,
    departement: tuple[str, ...] = ("75", "92", "93", "94"),
    center: tuple[float, float] = (-133583.39, 5971815.98),
    radius: float = 650000,
    startAngle: float = math.pi * (1 - 3.5 * 1 / 9),
    factor: float = 2,
) -> GeoDataFrame:
    """Zoom on parisian departements

    Args:
        departement (list, optional): list of departements to be moved, departements closest to Paris are selected by default

        center (tuple, optional): center point from which an offshore point is computed to move Parisian departements
        It should be defined as a (longitude, latitude) point in crs EPSG:3857

        radius (float, optional): radius used with center point to make offshore point, distance in meter

        startAngle (float, optional): start angle defining offshore point, by default it is pi * (1 - 2.5 * 1/9))

        factor (float, optional): make departements bigger or smaller.
        This parameter is used by shapely.affinity.scale function, please refer to its documentation to choose the value.

    Notes:
        by default zoom method focuses on the closest departements to Paris, but the function can be used to make a zoom on
        any departement anywhere on the map

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')
        >>> #
        >>> # Zoom on parisian departements
        >>> dfZoom = df.zoom()
    """

    if all(
        [x in gdf.columns for x in ["code_insee_du_departement", "geometry"]]
    ):
        zoomDep = gdf[
            gdf["code_insee_du_departement"].isin(departement)
        ].reset_index(drop=True)

        if len(zoomDep.index) > 0:
            _rescale_geom(zoomDep, factor=factor)
            end = Point(center[0] + radius, center[1])
            line = LineString([center, end])

            line = rotate(line, startAngle, origin=center, use_radians=True)
            endPoint = Point(line.coords[1])
            center = _get_center(zoomDep)

            xoff = endPoint.coords.xy[0][0] - center[0]
            yoff = endPoint.coords.xy[1][0] - center[1]

            zoomDep["geometry"] = zoomDep["geometry"].translate(
                xoff=xoff, yoff=yoff
            )

            gdf = pd.concat([gdf, zoomDep]).reset_index(drop=True)

    return gdf
