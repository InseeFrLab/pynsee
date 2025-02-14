from typing import Optional
from geopandas import GeoDataFrame, GeoSeries


def _get_center(
    gdf: GeoDataFrame, geocol: Optional[str] = None
) -> tuple[float, float]:
    """
    Get the center of the geometries in a GeoDataFrame.

    Note
    ----
    This function may be applied on a column that is *not* the
    default geometry (i.e. not a ``GeoSeries``).
    """
    geocol = geocol or gdf.geometry.name

    geoseries = (
        gdf.geometry
        if geocol == gdf.geometry.name
        else GeoSeries(gdf[geocol], crs=gdf.crs)
    )

    minxdf, maxydf, maxxdf, minydf = geoseries.total_bounds

    return (maxxdf + minxdf) / 2, (maxydf + minydf) / 2
