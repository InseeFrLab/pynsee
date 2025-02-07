# -*- coding: utf-8 -*-

import logging
import multiprocessing
import warnings
from typing import Optional, Union
from xml.etree import ElementTree

import requests
import tqdm
from shapely import MultiPolygon, Polygon

from pynsee.utils.save_df import save_df
from pynsee.utils.requests_session import PynseeAPISession

from .geofrdataframe import GeoFrDataFrame


logger = logging.getLogger(__name__)


@save_df(obj=GeoFrDataFrame, day_lapse_max=90)
def _get_geodata(
    dataset_id: str,
    polygon: Optional[Union[MultiPolygon, Polygon]] = None,
    update: bool = False,
    silent: bool = False,
    crs: str = "EPSG:3857",
    crsPolygon: str = "EPSG:4326",
    ignore_error: bool = True,
) -> GeoFrDataFrame:
    """
    Get geographical data with identifier and from IGN API

    Args:
        id (str): _description_
        polygon (Polygon, optional): Polygon used to constrain the area of interest. Defaults to None.
        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.
        crs (str, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.
        crsPolygon (str, optional): CRS used for `polygon`. Defaults to 'EPSG:4326'.
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

    if crsPolygon not in ("EPSG:3857", "EPSG:4326"):
        raise ValueError(
            "crsPolygon must be either 'EPSG:3857' or 'EPSG:4326'"
        )

    bbox = ""

    # add bounding box to link if polygon provided
    if polygon is not None:
        bounds = polygon.bounds
        bounds = [str(b) for b in bounds]

        if crsPolygon == "EPSG:3857":
            bounds = [
                bounds[0],
                bounds[1],
                bounds[2],
                bounds[3],
                "urn:ogc:def:crs:" + crsPolygon,
            ]
        else:
            bounds = [
                bounds[1],
                bounds[0],
                bounds[3],
                bounds[2],
                "urn:ogc:def:crs:" + crsPolygon,
            ]

        bbox = "&BBOX={}".format(",".join(bounds))

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

                warnings.warn(message, category=RuntimeWarning, stacklevel=1)

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

            maxstart = num_calls * count

            Nproc = min(num_calls, 6, multiprocessing.cpu_count())

            link = urldata.format(
                url=geoportail,
                typename=dataset_id,
                fmt=fmt,
                start="{start}",
                count="{count}",
                crs=crs,
            )

            args = (
                (link, session, count, maxstart, num_hits, i)
                for i in range(num_calls)
            )

            with multiprocessing.Pool(processes=Nproc) as pool:
                list_req = list(
                    tqdm.tqdm(
                        pool.imap_unordered(_make_request, args),
                        total=num_calls,
                    )
                )

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
            stacklevel=1,
        )

        return GeoFrDataFrame()

    gdf = GeoFrDataFrame.from_features(data, crs=crs)

    # drop data outside polygon
    if polygon is not None:
        if gdf.crs != crsPolygon:
            gdf = gdf.to_crs(crsPolygon)

        return (
            gdf.iloc[gdf.sindex.query(polygon, predicate="intersects")]
            .to_crs(crs)
            .reset_index(drop=True)
        )

    return gdf


def _make_request(
    arg: tuple[str, requests.Session, int, int, int, int]
) -> tuple[requests.Response, str]:
    """Make the request inside the multiprocessing.Pool"""
    urldata, session, count, maxstart, num_hits, i = arg

    start = i * count
    cnt = num_hits - start if num_hits - start <= count else count
    link = urldata.format(start=start, count=cnt)

    return session.get(link, verify=False), link


def _check_request_update_data(
    data: list,
    r: requests.Request,
    link: str,
    polygon: Optional[Union[MultiPolygon, Polygon]],
) -> None:
    """Check that the request succeeded and update"""
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
                "\nCheck that crsPolygon argument corresponds "
                "to polygon data!"
            )

        logger.error(msg)
