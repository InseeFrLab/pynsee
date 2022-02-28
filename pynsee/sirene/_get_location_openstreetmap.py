
import os
import sys
from datetime import datetime
from pathlib2 import Path
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd

from pynsee.sirene._make_dataframe_from_dict import _make_dataframe_from_dict

def _get_location_openstreetmap(query, session=None):

    if session is None:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

    api_link = "https://nominatim.openstreetmap.org/search.php?q={}&format=jsonv2&limit=1".format(query)
    # api_link = 'https://nominatim.openstreetmap.org/search?q=ZONE+INDUSTRIELLE+54980+BATILLY+FRANCE&format=json&limit=1'

    try:
        home = str(Path.home())
        user_agent = os.path.basename(home)
    except:
        user_agent = ""

    headers = {'User-Agent': 'python_package_pynsee_' + user_agent.replace("/", "")}

    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '', 'https': ''}

    results = session.get(api_link, proxies=proxies, headers=headers)
    data = results.json()

    list_dataframe = []

    for i in range(len(data)):
        idata = data[i]
        data_final = _make_dataframe_from_dict(idata)
        list_dataframe.append(data_final)

    data_final = pd.concat(list_dataframe).reset_index(drop=True)

    lat, lon, category, typeLoc, importance = (data_final["lat"][0], data_final["lon"][0], 
                                data_final["category"][0], data_final["type"][0],
                                data_final["importance"][0])

    return lat, lon, category, typeLoc, importance
