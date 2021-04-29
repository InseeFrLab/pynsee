from functools import lru_cache

@lru_cache(maxsize=None)
def _get_token():
    import os
    #from api_insee import ApiInsee
    
    from pynsee.utils._get_envir_token import _get_envir_token
    from pynsee.utils._get_token_from_insee import _get_token_from_insee

    token_envir = _get_envir_token()

    if token_envir is None:
        try:       
            # api = ApiInsee(
            #     key = os.environ.get('insee_key'),
            #     secret = os.environ.get('insee_secret')
            # )
            # token = api.auth.token.access_token
            token = _get_token_from_insee()
        except:
            token = None
    else:
        token = token_envir

    return(token)


