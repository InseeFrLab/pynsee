import pandas as pd
import math
from shapely.affinity import translate as trs
from shapely.affinity import rotate
from shapely.geometry import Point, LineString
import warnings
from shapely.errors import ShapelyDeprecationWarning

from pynsee.geodata._rescale_geom import _rescale_geom
from pynsee.geodata._get_center import _get_center


def zoom(
    self,
    departement=["75", "92", "93", "94"],
    center=(-133583.39, 5971815.98),
    radius=650000,
    startAngle=math.pi * (1 - 2.5 * 1 / 9),
    factor=2,
):
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

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
        df = self
        if all([x in df.columns for x in ["insee_dep", "geometry"]]):

            zoomDep = df[df["insee_dep"].isin(departement)].reset_index(drop=True)

            if len(zoomDep.index) > 0:

                zoomDep = _rescale_geom(df=zoomDep, factor=factor)
                end = Point(center[0] + radius, center[1])
                line = LineString([center, end])

                line = rotate(line, startAngle, origin=center, use_radians=True)
                endPoint = Point(line.coords[1])
                center = _get_center(zoomDep)

                xoff = endPoint.coords.xy[0][0] - center[0]
                yoff = endPoint.coords.xy[1][0] - center[1]

                zoomDep["geometry"] = zoomDep["geometry"].apply(
                    lambda x: trs(x, xoff=xoff, yoff=yoff)
                )
                df = pd.concat([self, zoomDep]).reset_index(drop=True)

        return df
