# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
import requests
import ast

from pynsee.utils._get_token import _get_token
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._wait_api_query_limit import _wait_api_query_limit


def _request_insee(api_url=None, sdmx_url=None, file_format='application/xml', print_msg=True):

    # sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
    # api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
    # api_url = 'https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRES/?firstNObservations=4&lastNObservations=1'

    keys = _get_credentials()

    try:
        pynsee_query_print = os.environ['pynsee_query_print']
    except:
        pass
    else:
        if pynsee_query_print == 'True':
            if api_url is not None:
                print('\n' + api_url)
            else:
                if sdmx_url is not None:
                    print('\n' + sdmx_url)

    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '', 'https': ''}

    # force sdmx use with a system variable
    try:
        pynsee_use_sdmx = os.environ['pynsee_use_sdmx']
        if pynsee_use_sdmx == "True":
            api_url = None
    except:
        pass

    # if api_url is provided, it is used first,
    # and the sdmx url is used as a backup in two cases
    # 1- when the token is missing
    # 2- if the api request fails

    # if api url is missing sdmx url is used

    if api_url is not None:

        if keys is not None:
            insee_key = keys['insee_key']
            insee_secret = keys['insee_secret']

            token = _get_token(insee_key, insee_secret)
        else:
            token = None

        if token is not None:
            headers = {'Accept': file_format,
                       'Authorization': 'Bearer ' + token}

            # avoid reaching the limit of 30 queries per minute from insee api
            _wait_api_query_limit(api_url)

            results = requests.get(api_url, proxies=proxies, headers=headers)
            
            success = True
            
            if 'status_code' not in dir(results):
                success = False
            else:    
                if results.status_code != 200:
                    success = False
            
            if success is True:                
                return(results)
            else:

                msg1 = "\n!!! An error occurred !!!"

                if print_msg:

                    print("{}".format(msg1))
                    print("Query : {}".format(api_url))

                if sdmx_url is not None:

                    results = requests.get(sdmx_url, proxies=proxies)

                    if print_msg:
                        print("\n!!! SDMX web service used instead of API !!!")

                    if results.status_code == 200:
                        return(results)
                    else:
                        raise ValueError(results.text + '\n' + sdmx_url)
                else:
                    if print_msg:                        
                        try:
                            print("Error %s\n" % results.status_code)                            
                        except:
                            pass

                    raise ValueError(results.text)
                                          
        else:
            # token is None
            commands = "\n\ninit_conn(insee_key='my_insee_key', insee_secret='my_insee_secret')\n"
            msg1 = "!!! Token missing, please check your credentials on api.insee.fr !!!\n"
            msg2 = "!!! Please do the following to use your credentials : {}".format(
                commands)
            msg3 = "\n!!! If your token still does not work, please try to clear the cache :\n from pynsee.utils import clear_all_cache; clear_all_cache() !!!\n"

            if sdmx_url is not None:
                msg4 = "\nSDMX web service used instead of API"
                if print_msg:
                    print("{}{}{}{}".format(msg1, msg2, msg3, msg4))

                results = requests.get(sdmx_url, proxies=proxies)

                if results.status_code == 200:
                    return(results)
                else:
                    raise ValueError(results.text + '\n' + sdmx_url)

            else:
                raise ValueError("{}{}{}".format(msg1, msg2, msg3))
    else:
        # api_url is None
        if sdmx_url is not None:
            results = requests.get(sdmx_url, proxies=proxies)

            if results.status_code == 200:
                return(results)
            else:
                raise ValueError(results.text + '\n' + sdmx_url)

        else:
            raise ValueError("!!! Error : urls are missing")
