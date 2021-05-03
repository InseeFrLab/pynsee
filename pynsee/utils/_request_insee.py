
import os
import requests
from pynsee.utils._get_token import _get_token
from pynsee.utils._wait_api_query_limit import _wait_api_query_limit

def _request_insee(api_url=None, sdmx_url=None, file_format='application/xml'): 

    # sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
    # api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
    # api_url = 'https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRES/?firstNObservations=4&lastNObservations=1'

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
            headers = {'Accept': file_format,
                       'Authorization': 'Bearer ' + token}
            
            # avoid reaching the limit of 30 queries per minute from insee api
            _wait_api_query_limit(api_url)

            results = requests.get(api_url, proxies = proxies, headers=headers)

            if results.status_code != 200:
                
                print("{}".format(api_url))
                
                msg1 = "\n!!! Wrong query or api.insee.fr error !!!"
#                msg2 = "\n!!! Please check your credentials and subscribe to all APIs!!!"
#                msg3 = "\n!!! If your token still does't work, please try to use pynsee.utils.clear_all_cache !!!"
#                print("{}{}{}".format(msg1, msg2, msg3))
                print("{}".format(msg1))

                if not sdmx_url is None:

                    results = requests.get(sdmx_url, proxies = proxies)
                    print("!!! SDMX web service used instead of API !!!")

                    if results.status_code != 200:
                        raise ValueError(results.text + '\n' + sdmx_url)
                else:
                    print("Error %s" % results.status_code)
                    
#                    m = re.search("ams\\:description\\>.*\\<\\/ams\\:description", results.text)
#                    if m:
#                        found = m.group(0)
#                        found2 = found.replace("description", "").replace("ams", "")
#                        print(found2)

        else:
            # token is None
            commands = "\nimport os\nos.environ['insee_key'] = 'my_key'\nos.environ['insee_secret'] = 'my_secret_key'"
            msg1 = "!!! Token missing, please check your credentials on api.insee.fr !!!\n"
            msg2 = "!!! Please do the following to use your credentials : {}".format(commands)
            msg3 = "\n!!! If your token still does not work, please try to use pynsee.utils.clear_all_cache !!!\n"
        
            if not sdmx_url is None:
                msg4 = "SDMX web service used instead of API"
                print("{}{}{}{}".format(msg1, msg2, msg3, msg4))
                # _warning_no_token(msg + msg2)
                results = requests.get(sdmx_url, proxies = proxies)
                if results.status_code != 200:
                    raise ValueError(results.text + '\n' + sdmx_url)
            else:
                raise ValueError("{}{}{}".format(msg1, msg2, msg3))
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
