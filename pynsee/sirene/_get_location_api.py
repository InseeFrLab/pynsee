
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

session.get(url)

def _get_location_api():

    api_link = "https://nominatim.openstreetmap.org/search.php?q=paris&format=jsonv2"

    q = "search?q=44310+LA+LIMOUZINIERE+FRANCE&format=json&limit=1"

    from pathlib import Path
    home = str(Path.home())
    

    