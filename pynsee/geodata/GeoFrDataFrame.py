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
        """Deprecated alias for `geometry`"""
        warnings.warn(
            message="`get_geom` is deprecated, please use the `geometry` "
            "property of the `GeoFrDataFrame` instead.",
            stacklevel=2,
        )

        return self.geometry

    def translate(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Apply translation for oversea territories.

        See: :func:`pynsee.geodata.translate.translate`.
        """
        from .translate import translate

        return translate(self, *args, **kwargs)

    def zoom(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Zoom for parisian departments.

        See: :func:`pynsee.geodata.zoom.zoom`.
        """
        from .zoom import zoom

        return zoom(self, *args, **kwargs)
