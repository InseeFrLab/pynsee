# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _get_temp_dir():
    import tempfile
    dirpath = tempfile.mkdtemp()
    return(dirpath)