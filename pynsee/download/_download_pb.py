import os
import requests
import urllib3

from tqdm import tqdm

import pynsee


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _download_pb(url: str, fname: str, total: int = None):
    """Useful function to get request with a progress bar

    Borrowed from
    https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51

    Arguments:
        url {str} -- URL for the source file
        fname {str} -- Destination where data will be written
    """
    proxies = {
        "http": os.environ.get("http_proxy", pynsee._config["http_proxy"]),
        "https": os.environ.get("https_proxy", pynsee._config["https_proxy"])
    }

    resp = requests.get(url, proxies=proxies, stream=True, verify=False)

    if total is None:
        total = int(resp.headers.get("content-length", 0))

    with open(fname, "wb") as file, tqdm(
        desc="Downloading: ",
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
        disable=pynsee._config["hide_progress"]
    ) as obj:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            obj.update(size)
