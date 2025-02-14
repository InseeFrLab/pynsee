import json
import os

import requests
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from pynsee.utils._warning_cached_data import _warning_cached_data


def _get_location_openstreetmap(
    query: str, session: requests.Session, update: bool = False
) -> tuple[float, float, str, str, float]:
    """
    Query a location using Nominatim and cache it on local disk.

    Parameters
    ----------
    query : str
        query, fo instance '2+Rue+DES+FRERES+BERTRAND+69200+VENISSIEUX+FRANCE'
    session : requests.Session
        requests.Session object used for the connection.
    update : bool, optional
        If False, will first try to restore previous data from disk. The
        default is False.

    Returns
    -------
    tuple[float, float, str, str, float]
        latitude, longitude, location category, location type, importance

    """
    api_link = (
        "https://nominatim.openstreetmap.org/search.php?"
        f"q={query}&format=jsonv2&limit=1"
    )

    insee_folder = _create_insee_folder()
    filename = os.path.join(insee_folder, f"{_hash(api_link)}.json")

    if update or not os.path.isfile(filename):
        results = session.get(api_link)
        data = results.json()

        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        with open(filename, "r") as f:
            data = json.load(f)

        _warning_cached_data(filename)

    data = data[0]
    return (
        float(data["lat"]),
        float(data["lon"]),
        data["category"],
        data["type"],
        data["importance"],
    )
