# -*- coding: utf-8 -*-

from functools import lru_cache
import warnings

from pynsee.geodata.get_geodata import get_geodata


@lru_cache(maxsize=None)
def get_population():
    """Get population data on all French communes (cities)

    Examples:
        >>> from pynsee.localdata import get_population
        >>> pop = get_population()
    """

    warnings.warn(
        "get_population is deprecated. Please use "
        "`from pynsee import get_geodata;get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:commune')` "
        "instead",
        category=FutureWarning,
    )

    df = get_geodata("ADMINEXPRESS-COG-CARTO.LATEST:commune")

    return df
