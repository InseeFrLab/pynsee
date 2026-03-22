# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import multiprocessing
import warnings
from typing import Any, Optional, Union
from xml.etree import ElementTree

import requests
from tqdm import tqdm
from pyproj.crs import CRS
from shapely import MultiPolygon, Polygon

from pynsee.utils.save_df import save_df
from pynsee.utils.requests_session import PynseeAPISession

from .geofrdataframe import GeoFrDataFrame


logger = logging.getLogger(__name__)


@save_df(cls=GeoFrDataFrame, day_lapse_max=90)
def _get_geodata(
    dataset_id: str,
    polygon: Optional[Union[MultiPolygon, Polygon]] = None,
    update: bool = False,
    silent: bool = False,
    crs: Any = "EPSG:3857",
    crs_polygon: Any = "EPSG:4326",
    ignore_error: bool = True,
) -> GeoFrDataFrame:
    """
    Get geographical data with identifier and from IGN API

    Args:
        id (str): _description_
        polygon (Polygon, optional): Polygon used to constrain the area of interest. Defaults to None.
        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.
        silent (bool, optional): whether to print warnings or not. Defaults to False.
        crs (any valid :class:`~pyproj.crs.CRS` entry, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.
        crs_polygon (any valid :class:`~pyproj.crs.CRS` entry, optional): CRS used for `polygon`. Defaults to 'EPSG:4326'.
        ignore_error (boo, optional): whether to ignore errors and return an empty GeoDataFrame. Defaults to True.

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')

    Returns: GeoFrDataFrame
    """
    crs = CRS.from_user_input(crs).to_string()
    crs_polygon = CRS.from_user_input(crs_polygon).to_string()

    if crs_polygon not in ("EPSG:3857", "EPSG:4326"):
        raise ValueError(
            "crs_polygon must be either 'EPSG:3857' or 'EPSG:4326'"
        )

    bbox = ""

    # add bounding box to link if polygon provided
    if polygon is not None:
        bounds = polygon.bounds
        bounds = [str(b) for b in bounds]

        if crs_polygon == "EPSG:3857":
            bounds = [
                bounds[0],
                bounds[1],
                bounds[2],
                bounds[3],
                "urn:ogc:def:crs:" + crs_polygon,
            ]
        else:
            bounds = [
                bounds[1],
                bounds[0],
                bounds[3],
                bounds[2],
                "urn:ogc:def:crs:" + crs_polygon,
            ]

        bbox = f"&BBOX={','.join(bounds)}"

    geoportail = "https://data.geopf.fr"
    fmt = "application/json"

    urlhits = (
        "{url}/wfs/ows?service=WFS&version=2.0.0"
        "&request=GetFeature&typenames={typename}&resultType=hits" + bbox
    )

    urldata = (
        "{url}/wfs/?service=WFS&version=2.0.0"
        "&request=GetFeature&typenames={typename}"
        "&outputFormat={fmt}&startIndex={start}&count={count}"
        "&srsName={crs}" + bbox
    )

    hits = urlhits.format(url=geoportail, typename=dataset_id)

    with PynseeAPISession() as session:
        try:
            data = session.get(hits, verify=False)
        except requests.exceptions.RequestException as exc:
            if ignore_error:
                message = "Request failed"
                res = exc.response

                if hasattr(res, "status_code"):
                    message += f" (error {res.status_code}): {res.reason}"
                else:
                    message += str(exc)

                message += f"\nFaulty URL: {hits}."

                warnings.warn(message, category=RuntimeWarning, stacklevel=2)

                return GeoFrDataFrame()

            raise exc

        root = ElementTree.fromstring(data.content)
        num_hits = int(root.attrib["numberMatched"])

        data = []
        count = 5000  # max items returned by https://data.geopf.fr/wfs

        # iterate if necessary
        if num_hits > count:
            num_calls = num_hits // count

            if num_calls * count < num_hits:
                num_calls += 1

            n_proc = min(num_calls, 7, multiprocessing.cpu_count())

            link = urldata.format(
                url=geoportail,
                typename=dataset_id,
                fmt=fmt,
                start="{start}",
                count="{count}",
                crs=crs,
            )

            args = ((link, session, count, i) for i in range(num_calls))

            with ThreadPoolExecutor(max_workers=n_proc) as pool:

                submitted = [pool.submit(_make_request, x) for x in args]
                list_req = [
                    future.result()
                    for future in tqdm(
                        as_completed(submitted), total=num_calls
                    )
                ]

            for r, link in list_req:
                _check_request_update_data(data, r, link, polygon)
        else:
            link = urldata.format(
                url=geoportail,
                typename=dataset_id,
                fmt=fmt,
                start=0,
                count=num_hits,
                crs=crs,
            )

            r = session.get(link, verify=False)

            _check_request_update_data(data, r, link, polygon)

    if not data:
        warnings.warn(
            "Error 200: Valid request returned empty result",
            category=RuntimeWarning,
            stacklevel=2,
        )

        return GeoFrDataFrame()

    gdf = GeoFrDataFrame.from_features(data, crs=crs)

    # drop data outside polygon
    if polygon is not None:
        if gdf.crs != crs_polygon:
            gdf = gdf.to_crs(crs_polygon)

        return (
            gdf.iloc[gdf.sindex.query(polygon, predicate="intersects")]
            .to_crs(crs)
            .reset_index(drop=True)
        )

    return gdf


def _make_request(
    arg: tuple[str, requests.Session, int, int, int],
) -> tuple[requests.Response, str]:
    """Make the request inside the multiprocessing.Pool"""
    urldata, session, count, i = arg

    start = i * count
    link = urldata.format(start=start, count=count)

    return session.get(link, verify=False), link


def _check_request_update_data(
    data: list,
    r: requests.Request,
    link: str,
    polygon: Optional[Union[MultiPolygon, Polygon]],
) -> None:
    """
    Check that the request succeeded and update `data` inplace.
    """
    if not r.ok:
        raise requests.RequestException(
            f"The following query raise an error {r.status_code}: {link}"
        )

    json = r.json()["features"]

    if json:
        data.extend(json)
    else:
        msg = f"Query is correct but no data found: {link}"

        if polygon is not None:
            msg += (
                "\nCheck that crs_polygon argument corresponds "
                "to polygon data!"
            )

        logger.error(msg)
