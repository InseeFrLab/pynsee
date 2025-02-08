from .geofrdataframe import GeoFrDataFrame


def get_geom(gdf: GeoFrDataFrame):
    """Extract a shape (Polygon, Point ...) from a GeoFrDataFrame

    .. deprecated:: 0.2.0

        Use :meth:`GeoFrDataFrame.geometry` instead.

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')
        >>> #
        >>> # Extract a polygon from the GeoDataframe
        >>> geo = df.get_geom()
    """
    return gdf.get_geom()
