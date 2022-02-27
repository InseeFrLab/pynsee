
import pyproj
from shapely.ops import transform

def _convert_polygon(geo,crs_in='EPSG:4326', crs_out='EPSG:3857'):
    
    crsIn = pyproj.CRS(crs_in)
    crsOut = pyproj.CRS(crs_out)

    project = pyproj.Transformer.from_crs(crsIn, crsOut, always_xy=True).transform
    geo_converted = transform(project, geo)
    
    return geo_converted

def _convert_polygon_list(i):    
    return _convert_polygon(list_geom[i])

def _set_global_translate_overseas(args):
    global list_geom
    list_geom = args[0]


