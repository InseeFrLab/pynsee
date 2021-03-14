from functools import lru_cache
import warnings

# @lru_cache(maxsize=None)
# def _warning_api_success():
#     print("Insee API used")

# @lru_cache(maxsize=None)
# def _warning_api_failure():
#     msg1 = "\n!!! Error : check your subscription to api.insee.fr"
#     #msg2 = "Due to an error the sdmx service is used instead of the api!!!\n"
#     #print(msg1 + "\n" + msg2)
#     print(msg1 + "\n" )

@lru_cache(maxsize=None)
def _warning_no_token(msg):
    warnings.warn(msg)

def _request_insee(api_url=None, sdmx_url=None):

    import os, re
    import requests
    from ._get_token import _get_token

    # sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
    # api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"


    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '','https': ''}

    # if api_url is provided, it is used first,
    # and the sdmx url is used as a backup in two cases
    # 1- when the token is missing
    # 2- if the api request fails

    # if api url is missing sdmx url is used

    if not api_url is None:

        token = _get_token()

        if not token is None:
            headers = {'Accept': 'application/xml',
                        'Authorization': 'Bearer ' + token}

            results = requests.get(api_url, proxies = proxies, headers=headers)

            if results.status_code != 200:
                    
                print("!!! Wrong query or api.insee.fr error !!!\n!!! Please check your credentials and subscribe to all APIs!!!")

                if not sdmx_url is None:

                    results = requests.get(sdmx_url, proxies = proxies)
                    print("!!! SDMX web service used instead of API !!!")

                    if results.status_code != 200:
                        raise ValueError(results.text + '\n' + sdmx_url)
                else:
                    print("Error %s" % results.status_code)
                    
                    m = re.search("ams\\:description\\>.*\\<\\/ams\\:description", results.text)
                    if m:
                        found = m.group(0)
                        found2 = found.replace("description", "").replace("ams", "")
                        print(found2)

        else:
            # token is None

            msg = "!!! Token missing, please check your credentials on api.insee.fr !!!\n"
            if not sdmx_url is None:
                msg2 = "SDMX web service used instead of API"
                print(msg + msg2)
                # _warning_no_token(msg + msg2)
                results = requests.get(sdmx_url, proxies = proxies)
                if results.status_code != 200:
                    raise ValueError(results.text + '\n' + sdmx_url)
            else:
                raise ValueError(msg)
    else:
        #api_url is None
        if not sdmx_url is None:
            results = requests.get(sdmx_url, proxies = proxies)

            if results.status_code != 200:
                    raise ValueError(results.text + '\n' + sdmx_url)
        else:
            raise ValueError("!!! Error : urls are missing")
    try:
        return(results)
    except:
        raise ValueError("Error")
