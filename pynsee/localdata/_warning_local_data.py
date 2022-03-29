# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

@lru_cache(maxsize=None)
def _warning_local_data():
    print("!!! This function renders only package's internal data,\nit might not be the most up-to-date\nHave a look at api.insee.fr !!!")
