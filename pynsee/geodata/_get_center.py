from geopandas import GeoDataFrame
from ._extract_bounds import _extract_bounds


def _get_center(gdf: GeoDataFrame, col: str = "geometry"):
    """Get the center of the geometries in a GeoDataFrame"""
    geo = getattr(gdf, col)

    return _extract_center(geo)


def _extract_center(geo):
    maxxdf = max(_extract_bounds(geom=geo, var="maxx"))
    minxdf = min(_extract_bounds(geom=geo, var="minx"))
    maxydf = max(_extract_bounds(geom=geo, var="maxy"))
    minydf = min(_extract_bounds(geom=geo, var="miny"))

    return ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)
