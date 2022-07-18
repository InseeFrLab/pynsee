# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import tempfile
from functools import lru_cache


@lru_cache(maxsize=None)
def _get_temp_dir():

    dirpath = tempfile.mkdtemp()
    return dirpath
