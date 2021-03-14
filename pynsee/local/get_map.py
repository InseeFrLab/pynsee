# -*- coding: utf-8 -*-

def get_map(geo):
    
    import geopandas as gpd
    
    from pynsee.local.get_map_link import get_map_link
    
    map = gpd.read_file(get_map_link(geo))

    return(map)