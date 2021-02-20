
def _get_token():
    import os
    from api_insee import ApiInsee
    try:       
        api = ApiInsee(
            key = os.environ.get('insee_key'),
            secret = os.environ.get('insee_secret')
        )
        token = api.auth.token.access_token
    except:
        token = None
    return(token)


