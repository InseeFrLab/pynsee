from geopandas import GeoDataFrame


def _get_center(gdf: GeoDataFrame):
    """Get the center of the geometries in a GeoDataFrame"""
    bounds = gdf.bounds

    maxxdf = bounds.maxx.max()
    minxdf = bounds.minx.min()
    maxydf = bounds.maxy.max()
    minydf = bounds.miny.min()

    return ((maxxdf + minxdf) / 2, (maxydf + minydf) / 2)
