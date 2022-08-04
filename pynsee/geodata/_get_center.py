from pynsee.geodata._extract_bounds import _extract_bounds
from pynsee.geodata._get_geom import _get_geom


def _get_center(df, col="geometry"):

    geo = _get_geom(df, col=col)

    center = _extract_center(geo)

    return center


def _extract_center(geo):

    maxxdf = max(_extract_bounds(geom=geo, var="maxx"))
    minxdf = min(_extract_bounds(geom=geo, var="minx"))
    maxydf = max(_extract_bounds(geom=geo, var="maxy"))
    minydf = min(_extract_bounds(geom=geo, var="miny"))
    center = ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)

    return center
