from geopandas import GeoDataFrame, GeoSeries


def _get_center(gdf: GeoDataFrame, geocol="geometry"):
    """Get the center of the geometries in a GeoDataFrame"""
    geoseries = (
        gdf[geocol]
        if geocol == "geometry"
        else GeoSeries(gdf[geocol], crs=gdf.crs)
    )

    bounds = geoseries.bounds

    maxxdf = bounds.maxx.max()
    minxdf = bounds.minx.min()
    maxydf = bounds.maxy.max()
    minydf = bounds.miny.min()

    return ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)
