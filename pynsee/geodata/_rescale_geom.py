
from shapely.affinity import scale
from shapely.geometry import MultiPolygon

def _rescale_geom(geo, factor=1, center=None):
    
    list_geoms = []
    
    if center is None:
        center = "center"    

    for i in range(len(geo.geoms)):

        list_geoms +=  [scale(
            geom =  geo.geoms[i],
            xfact= factor,
            yfact= factor,
            zfact=1.0,
            origin=center)]

    return MultiPolygon(list_geoms) 