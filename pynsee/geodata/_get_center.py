
from pynsee.geodata._extract_bounds import _extract_bounds

def _get_center(geo):
    
    maxxdf = max(_extract_bounds(polygon=geo, var='maxx'))
    minxdf = min(_extract_bounds(polygon=geo, var='minx'))
    maxydf = max(_extract_bounds(polygon=geo, var='maxy'))
    minydf = min(_extract_bounds(polygon=geo, var='miny'))
    center = ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)

    return center