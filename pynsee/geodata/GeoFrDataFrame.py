import warnings

from geopandas import GeoDataFrame


class GeoFrDataFrame(GeoDataFrame):
    """Class for handling GeoDataFrames built from IGN's geographical data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoFrDataFrame


    def get_geom(self):
        ''' Deprecated alias for `geometry` '''
        warnings.warn(
            message="`get_geom` is deprecated, please use the `geometry` "
                "property instead.",
            stacklevel=2
        )
        return self.geometry

    from pynsee.geodata.translate import translate
    from pynsee.geodata.zoom import zoom
