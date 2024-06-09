
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _get_requests_headers():

    username = os.environ.get("USERNAME", "username")
    
    headers = {
        'User-Agent': f"python_pynsee_{username}"
    }
    return headers

def _get_requests_session():
    
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def _get_requests_proxies():
    
    proxies = {"http": os.environ.get("http_proxy", ""),
               "https": os.environ.get("https_proxy", "")}
        
    return proxies