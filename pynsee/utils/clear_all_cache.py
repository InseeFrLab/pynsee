# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import functools
import gc


def clear_all_cache():
    """Clear the cache of all functions

    Notes:
        If the credentials provided fail to get a token from api.insee.fr even after a double check,
        try to clear the cache as the output of the function retrieving the token is cached even
        it is an error.

    Examples:
        >>> from pynsee.utils import clear_all_cache
        >>> clear_all_cache()
    """
    gc.collect()
    wrappers = [
        a for a in gc.get_objects() if isinstance(a, functools._lru_cache_wrapper)
    ]

    for wrapper in wrappers:
        wrapper.cache_clear()
