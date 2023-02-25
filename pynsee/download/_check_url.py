from datetime import date
import requests
import re
import os
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _check_url(url):
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["https_proxy"]}
    except:
        proxies = {"http": "", "https": ""}
        
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    check = session.get(url, proxies=proxies, stream=True, verify=False)

    if check.status_code == 200:
        return url
    else:
        print(f"File not found on insee.fr:\n{url}")
        print("Please open an issue on:\nhttps://github.com/InseeFrLab/pynsee")
        
        try:
            list_string_split = url.split("/")
            filename = list_string_split[-1]

            list_potential_dates = []

            def get_close_dates_list(start_year, timespan=10):   

                start_year = int(start_year)    
                start_year_short = int(str(start_year)[-2:])

                list_close_year = list(range(start_year, start_year + timespan)) + \
                                    list(range(start_year, start_year - timespan, -1)) + \
                                    list(range(start_year_short, start_year_short + timespan)) + \
                                    list(range(start_year_short, start_year_short - timespan, -1)) 

                list_close_year = [str(y) for y in list_close_year]

                return list_close_year

            datefile = re.findall("2\d{3}|\d{2}", filename)[0]

            list_potential_dates += get_close_dates_list(datefile)

            current_year = date.today().year

            list_potential_dates += get_close_dates_list(current_year)
            list_potential_dates = list(dict.fromkeys(list_potential_dates))        

            for d in list_potential_dates:

                filename2 = filename.replace(str(datefile), str(d))
                url2 = "/".join(
                    list_string_split[: (len(list_string_split) - 1)] + [filename2]
                )
                results = session.get(url2, proxies=proxies, stream=True, verify=False)

                if results.status_code == 200:
                    break

                if d == list_potential_dates[-1]:
                    print(f"No other similar files have been found")
                    url2 = url
        except:
            print(f"Error raised while trying to find another similar file")
        
        if 'url2' in locals():
            if url != url2:
                print(f"The following file has been used instead:\n{url2}")
        else:
            url2 = url
        
        return url2
            
        
        
        

