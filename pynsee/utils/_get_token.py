# Copyright : INSEE, 2021

from functools import lru_cache

from pynsee.utils._get_envir_token import _get_envir_token
from pynsee.utils._get_token_from_insee import _get_token_from_insee


@lru_cache(maxsize=None)
def _get_token(insee_key, insee_secret):

    token_envir = _get_envir_token()

    if token_envir is None:
        try:
            token = _get_token_from_insee(insee_key, insee_secret)
        except:
            token = None
    else:
        token = token_envir

    return token
