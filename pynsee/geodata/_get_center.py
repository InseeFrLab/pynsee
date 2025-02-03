from ._extract_bounds import _extract_bounds
from .GeoFrDataFrame import GeoFrDataFrame


def _get_center(gdf: GeoFrDataFrame, col: str = "geometry"):

    geo = getattr(gdf, col)

    center = _extract_center(geo)

    return center


def _extract_center(geo):

    maxxdf = max(_extract_bounds(geom=geo, var="maxx"))
    minxdf = min(_extract_bounds(geom=geo, var="minx"))
    maxydf = max(_extract_bounds(geom=geo, var="maxy"))
    minydf = min(_extract_bounds(geom=geo, var="miny"))
    center = ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)

    return center
