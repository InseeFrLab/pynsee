import warnings
from typing import Union

from pandas import DataFrame
from geopandas import GeoDataFrame


class GeoFrDataFrame(GeoDataFrame):
    """Class for handling GeoDataFrames built from IGN's geographical data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoFrDataFrame

    def _constructor_from_mgr(
        self, mgr, axes
    ) -> Union[DataFrame, "GeoFrDataFrame"]:
        """Patch to avoid class change"""
        obj = super()._constructor_from_mgr(mgr, axes)

        if isinstance(obj, GeoDataFrame):
            obj.__class__ = GeoFrDataFrame

        return obj

    def __getitem__(self, key):
        """
        Patch to avoid class change.
        """
        result = super().__getitem__(key)

        if isinstance(result, GeoDataFrame):
            result.__class__ = GeoFrDataFrame

        return result

    def copy(self, deep: bool = True) -> "GeoFrDataFrame":
        """Patch to avoid class change"""
        copied = super().copy(deep=deep)
        copied.__class__ = GeoFrDataFrame
        return copied

    def get_geom(self):
        """
        Deprecated alias for `geometry`.

        .. deprecated:: 0.2.0

            Use :meth:`GeoFrDataFrame.geometry` instead.

        """
        warnings.warn(
            "`get_geom` is deprecated, please use the `geometry` "
            "property of the `GeoFrDataFrame` instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        return self.geometry

    def transform_overseas(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Apply translation and zoom to oversea territories.

        See: :func:`pynsee.geodata.transform_overseas`.
        """
        from .translate_and_zoom import transform_overseas

        return transform_overseas(self, *args, **kwargs)

    def translate(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Deprecated alias of `transform_overseas`.
        This will switch to the normal behavior of
        :meth:`GeoDataFrame.translate` in ``pynsee >= 0.3``

        .. deprecated:: 0.2.0

            Use :meth:`GeoFrDataFrame.transform_overseas` instead.
        """
        warnings.warn(
            "`translate` will switch to the default `GeoDataFrame` "
            "behavior in the next release. Please use `transform_overseas` "
            "instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        return self.transform_overseas(*args, **kwargs)

    def zoom(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Zoom for parisian departments.

        See: :func:`pynsee.geodata.zoom.zoom`.
        """
        from .translate_and_zoom import zoom

        return zoom(self, *args, **kwargs)
