from tqdm import tqdm


from pynsee.utils.requests_session import PynseeAPISession


def _download_pb(url: str, fname: str, total: int = None):
    """Useful function to get request with a progress bar

    Borrowed from
    https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51

    Arguments:
        url {str} -- URL for the source file
        fname {str} -- Destination where data will be written
    """

    with PynseeAPISession() as s:
        resp = s.get(url, stream=True, verify=False)

    if total is None:
        total = int(resp.headers.get("content-length", 0))

    with (
        open(fname, "wb") as file,
        tqdm(
            desc="Downloading: ",
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as obj,
    ):
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            obj.update(size)
