# -*- coding: utf-8 -*-
from functools import lru_cache


@lru_cache(maxsize=None)
def _warning_cached_data(file):
    print("Previously saved data used\n{}\nSet update=True to get the most up-to-date data".format(file))
