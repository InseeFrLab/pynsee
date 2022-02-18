
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString, MultiPoint

class GeoDataframe(pd.DataFrame):
    """Class for handling dataframes built from IGN's geographical data

    """    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoDataframe

    from pynsee.geodata.get_geom import get_geom
