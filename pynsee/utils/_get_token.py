# Copyright : INSEE, 2021

import os
from typing import Optional

import pynsee
from pynsee.utils._get_token_from_insee import _get_token_from_insee


def _get_token(
    insee_key: Optional[str] = None,
    insee_secret: Optional[str] = None
):
    '''
    Get the token.

    The environment variable `insee_token` is prioritized if it exists, then
    comes the configuration variable.
    Finally, if none of these are set, query the token from the INSEE server
    based on the key and secret.
    '''
    token = os.environ.get("insee_token", pynsee.get_config("insee_token"))

    if token is None:
        try:
            token = _get_token_from_insee(insee_key, insee_secret)
        except Exception:
            token = None

    return token
