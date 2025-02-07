from typing import Optional

from geopandas import GeoDataFrame, GeoSeries

from ._get_center import _get_center


def _rescale_geom(
    gdf: GeoDataFrame,
    factor: float,
    geocol: str = "geometry",
    center: Optional[tuple[float, float]] = None,
) -> None:
    """Rescale geometries of a GeoDataFrame inplace."""
    center = center or _get_center(gdf, geocol)

    geoseries = (
        gdf[geocol]
        if geocol == "geometry"
        else GeoSeries(gdf[geocol], crs=gdf.crs)
    )

    gdf.loc[:, geocol] = geoseries.scale(
        xfact=factor,
        yfact=factor,
        zfact=1.0,
        origin=center,
    )
