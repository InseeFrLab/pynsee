# Copyright : INSEE, 2021

import os
from functools import lru_cache

import pynsee
from pynsee.utils._get_token_from_insee import _get_token_from_insee


@lru_cache(maxsize=None)
def _get_token(insee_key, insee_secret):

    token = os.environ.get("insee_token", pynsee._config["token"])

    if token is None:
        try:
            token = _get_token_from_insee(insee_key, insee_secret)
        except Exception:
            token = None

    return token
