import warnings
from typing import Union

import numpy as np
from pandas import DataFrame
from geopandas import GeoDataFrame, GeoSeries


class GeoFrDataFrame(GeoDataFrame):
    """
    Class for handling GeoDataFrames built from IGN's geographical data.
    It inherits from :class:`~geopandas.GeoDataFrame`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoFrDataFrame

    def _constructor_from_mgr(
        self, mgr, axes
    ) -> Union[DataFrame, "GeoFrDataFrame"]:
        """Patch to avoid class change."""
        obj = super()._constructor_from_mgr(mgr, axes)

        if isinstance(obj, GeoDataFrame):
            obj.__class__ = GeoFrDataFrame

        return obj

    def __getitem__(self, key):
        """Patch to avoid class change."""
        result = super().__getitem__(key)

        if isinstance(result, GeoDataFrame):
            result.__class__ = GeoFrDataFrame

        return result

    def copy(self, deep: bool = True) -> "GeoFrDataFrame":
        """Copy the :class:`GeoFrDataFrame` object."""
        # Patch to avoid class change
        copied = super().copy(deep=deep)
        copied.__class__ = GeoFrDataFrame
        return copied

    def get_geom(self):
        """
        Return the combination of all geometries in the
        :class:`GeoFrDataFrame`.

        .. deprecated:: 0.2.0

            Use :attr:`~geopandas.GeoDataFrame.geometry` instead and call
            :func:`~geopandas.GeoSeries.union_all` on it.
            See also the `documentation of geopandas <https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe>`_.

        Example
        -------

        >>> geo = gdf.geometry.union_all()
        """
        warnings.warn(
            "`get_geom` is deprecated, please use the `geometry` "
            "property of the `GeoFrDataFrame` instead. Then call "
            ":func:`~geopandas.GeoSeries.union_all` on it.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self.geometry.union_all()

    def transform_overseas(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Apply translation and zoom to oversea territories.

        See: :func:`pynsee.geodata.transform_overseas`.
        """
        from .translate_and_zoom import transform_overseas

        return transform_overseas(self, *args, **kwargs)

    def translate(self, *args, **kwargs) -> Union[GeoSeries, "GeoFrDataFrame"]:
        """
        This function is a deprecated alias of
        :meth:`~GeoFrDataFrame.transform_overseas`.
        It will try to guess whether you want to run `transform_overseas`
        or the real :meth:`GeoDataFrame.translate` depending on the
        arguments that were passed.
        If no arguments are passed, it will run `transform_overseas`.

        .. warning::

            Starting with ``pynsee >= 0.3.0``, this function will only
            run :meth:`GeoSeries.translate`. Do switch to
            :meth:`~GeoFrDataFrame.transform_overseas` if this is what
            you wanted to run.
        """
        run_super_translate = False

        if args and isinstance(args[0], (int, np.integer, float)):
            run_super_translate = True
        elif kwargs and ("xoff" in kwargs or "yoff" in kwargs):
            run_super_translate = True

        if run_super_translate:
            return super().translate(*args, **kwargs)

        warnings.warn(
            "`translate` will switch to the default `GeoDataFrame.translate` "
            "behavior in the next release. Please use `transform_overseas` "
            "instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self.transform_overseas(*args, **kwargs)

    def zoom(self, *args, **kwargs) -> "GeoFrDataFrame":
        """
        Zoom for parisian departments.

        See: :func:`pynsee.geodata.zoom`.
        """
        from .translate_and_zoom import zoom

        return zoom(self, *args, **kwargs)
