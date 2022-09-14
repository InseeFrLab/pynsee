from datetime import date
import requests
import re
import os
import urllib3



def _check_url(url):
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["https_proxy"]}
    except:
        proxies = {"http": "", "https": ""}

    check = requests.get(url, proxies=proxies, stream=True, verify=False)

    if check.status_code == 200:
        return url
    else:

        list_string_split = url.split("/")
        filename = list_string_split[len(list_string_split) - 1]

        dates = re.findall("2\d{3}|\d{2}", filename)
        current_year = date.today().year
        current_year_short = int(str(current_year)[-2:])

        list_close_year = list(range(current_year - 3, current_year + 3)) + list(
            range(current_year_short - 3, current_year_short + 3)
        )
        list_close_year = [str(y) for y in list_close_year]

        dates = [y for y in dates if str(y) in list_close_year]
        datefile = int(dates[len(dates) - 1])

        list_potential_dates = [datefile + 1] + list(range(datefile - 3, datefile + 3))

        print(f"File not found on insee.fr:\n{url}")

        print("Please open an issue on:\nhttps://github.com/InseeFrLab/Py-Insee-Data")

        for d in list_potential_dates:

            filename2 = filename.replace(str(datefile), str(d))
            url2 = "/".join(
                list_string_split[: (len(list_string_split) - 1)] + [filename2]
            )

            results = requests.get(url2, proxies=proxies, stream=True, verify=False)
            if results.status_code == 200:
                print(f"Following file has been used instead:\n{url2}")
                return url2

        raise ValueError("Please, report this issue")
