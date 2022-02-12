

from shapely.affinity import scale
from pynsee.geodata._extract_bounds import _extract_bounds

def _rescale_geom(df, factor):
    maxxdf = max(_extract_bounds(geom=df['geometry'], var='maxx'))
    minxdf = min(_extract_bounds(geom=df['geometry'], var='minx'))
    maxydf = max(_extract_bounds(geom=df['geometry'], var='maxy'))
    minydf = min(_extract_bounds(geom=df['geometry'], var='miny'))
    center = ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)
    
    list_geoms = []
    for i in range(len(df['geometry'])):
        list_geoms +=  [scale(
            geom =  df.loc[i, 'geometry'],
            xfact=factor,
            yfact=factor,
            zfact=1.0,
            origin=center)]
    
    df['geometry'] = list_geoms

    return(df) 