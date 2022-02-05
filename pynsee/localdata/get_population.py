# -*- coding: utf-8 -*-

from functools import lru_cache
import os
import zipfile
import pkg_resources
import pandas as pd

from pynsee.geodata.get_geodata import get_geodata

@lru_cache(maxsize=None)
def get_population():
    """Get population data on all French communes (cities)

    Examples:
        >>> from pynsee.localdata import get_population
        >>> pop = get_population()
    """
   
    df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:commune')

    return(df)
