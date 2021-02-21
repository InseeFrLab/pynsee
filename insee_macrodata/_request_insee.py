from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_api_success():
    print("Insee API used")

@lru_cache(maxsize=None)
def _warning_api_failure():
    msg1 = "\n!!! Warning : check your subscription to api.insee.fr"
    msg2 = "Due to an error the sdmx service is used instead of the api!!!\n"
    print(msg1 + "\n" + msg2)

@lru_cache(maxsize=None)
def _warning_no_token():
    msg1 = "\n!!! Warning : check your subscription to api.insee.fr"
    msg2 = "The sdmx service you are using may be deprecated !!!\n"
    print(msg1 + "\n" + msg2)   

def _request_insee(api_url, sdmx_url=None):

    import os
    import requests
    from ._get_token import _get_token

    proxies = {'http': os.environ.get('http'),
               'https': os.environ.get('https')}
        
    token = _get_token()
  
    if not token is None:
        headers = {'Accept': 'application/xml',
                    'Authorization': 'Bearer ' + token}
        try:
            _warning_api_success()
            results = requests.get(api_url, proxies = proxies, headers=headers)
        except:
            _warning_api_failure()
            results = requests.get(sdmx_url, proxies = proxies)
    else:
        if not sdmx_url is None:
            _warning_no_token()         
            results = requests.get(sdmx_url, proxies = proxies)
        else:
            print("!!! Error : token missing, check your keys correspond to your api.insee.fr account credentials")

    
    return(results)
