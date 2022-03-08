
from pynsee.geodata._extract_bounds import _extract_bounds

def _get_center(df):
    
    geo = df.get_geom()
    
    center = _extract_center(geo)

    return center

def _extract_center(geo)
    
    maxxdf = max(_extract_bounds(geom=geo, var='maxx'))
    minxdf = min(_extract_bounds(geom=geo, var='minx'))
    maxydf = max(_extract_bounds(geom=geo, var='maxy'))
    minydf = min(_extract_bounds(geom=geo, var='miny'))
    center = ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)
    
    return center
