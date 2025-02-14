from typing import Optional

from geopandas import GeoDataFrame

from ._get_center import _get_center


def _rescale_geom(
    gdf: GeoDataFrame,
    factor: float,
    center: Optional[tuple[float, float]] = None,
) -> None:
    """Rescale geometries of a GeoDataFrame inplace."""
    center = center or _get_center(gdf)

    gdf.loc[:, gdf.geometry.name] = gdf.geometry.scale(
        xfact=factor,
        yfact=factor,
        zfact=1.0,
        origin=center,
    )
