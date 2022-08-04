from pynsee.geodata._get_geom import _get_geom


def get_geom(self):
    """Extract a shape (Polygon, Point ...) from a GeoFrDataFrame

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

    geo = _get_geom(self)

    return geo
