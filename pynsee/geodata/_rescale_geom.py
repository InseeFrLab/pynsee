from geopandas import GeoDataFrame, GeoSeries

from ._get_center import _get_center


def _rescale_geom(gdf: GeoDataFrame, factor: float, geocol: str = "geometry"):
    center = _get_center(gdf, geocol)

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

    return gdf
