import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString, MultiPoint


def get_geom(self):
    """Extract a shape (Polygon, Point ...) from a GeoDataframe

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')
        >>> # 
        >>> # Extract a polygon from the GeoDataframe
        >>> geo = df.get_geom()
    """        

    self = self.reset_index(drop=True)
    
    if 'geometry' in self.columns:
        geoList = []
        geoListType = []

        none_detected = False

        for i in range(len(self.index)):
            poly = self['geometry'][i]                
            if type(poly) in [Polygon, Point, LineString]:
                geoList += [poly]
                geoListType.append(type(poly))
            elif type(poly) in [MultiPolygon, MultiLineString, MultiPoint]:
                for j in range(len(poly.geoms)):
                    geoList += [poly.geoms[j]]
                geoListType.append(type(poly))
            else:
                none_detected = True
        
        if none_detected:
            shapes = ["MultiPolygon", "MultiLineString", "MultiPoint"] + ["Polygon", "Point", "LineString"]
            print('!!! one shape in geometry column is not among supported shapely classes or is None:\n %s' % ', '.join(shapes))

        geoListType = list(dict.fromkeys(geoListType))

        if all([x in [MultiPolygon, Polygon] for x in geoListType]):
            geo = MultiPolygon(geoList)
        elif all([x in [MultiPoint, Point] for x in geoListType]):
            geo = MultiPoint(geoList)
        elif all([x in [MultiLineString, LineString] for x in geoListType]):
            geo = MultiLineString(geoList)
        else:
            raise ValueError('!!! geometry column mixes shapely classes !!!')     
    else:
        raise ValueError('!!! geometry column is missing !!!')

    return geo