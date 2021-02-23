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
    idbank_list = pd.read_csv(data_file, encoding = 'latin-1',
                              quotechar='"', sep=',', header = [0], index_col = 0,
                              dtype=str, usecols = [0,1,2,538,539])
    idbank_list = idbank_list[["nomflow", "idbank", "cleFlow", "title_fr", "title_en"]]
    return idbank_list