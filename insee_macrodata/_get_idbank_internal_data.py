# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 21:15:52 2021

@author: XLAPDO
"""

import pkg_resources
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=None)
def _get_idbank_internal_data():
    data_file = pkg_resources.resource_stream(__name__, 'data/idbank_list_internal.csv')
    return pd.read_csv(data_file, encoding = 'latin-1', dtype=str)