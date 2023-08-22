import json
import os
import requests

from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import pandas as pd

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict
from pynsee.utils._warning_cached_data import _warning_cached_data


def _get_location_openstreetmap(query, session=None, update=False):

    if session is None:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    api_link = "https://nominatim.openstreetmap.org/search.php?" \
        f"q={query}&format=jsonv2&limit=1"

    insee_folder = _create_insee_folder()
    filename = os.path.join(insee_folder, f"{_hash(api_link)}.json")

    try:
        home = str(Path.home())
        user_agent = os.path.basename(home)
    except Exception:
        user_agent = ""

    headers = {"User-Agent": "python_package_pynsee_" + user_agent.replace("/", "")}

    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["https_proxy"]}
    except Exception:
        proxies = {"http": "", "https": ""}

    data = None

    if update or not os.path.isfile(filename):
        results = session.get(api_link, proxies=proxies, headers=headers)
        data = results.json()

        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        with open(filename, "r") as f:
            data = json.load(f)

        _warning_cached_data(filename)

    list_dataframe = []

    for i in range(len(data)):
        idata = data[i]
        data_final = _make_dataframe_from_dict(idata)
        list_dataframe.append(data_final)

    data_final = pd.concat(list_dataframe).reset_index(drop=True)

    lat, lon, category, typeLoc, importance = (
        data_final["lat"][0],
        data_final["lon"][0],
        data_final["category"][0],
        data_final["type"][0],
        data_final["importance"][0],
    )

    return lat, lon, category, typeLoc, importance
