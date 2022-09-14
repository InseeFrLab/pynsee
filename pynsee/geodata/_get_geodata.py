# -*- coding: utf-8 -*-

import time
import pandas as pd
import requests
import os
import multiprocessing
import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path
import urllib3

from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.geodata._get_bbox_list import _get_bbox_list
from pynsee.geodata._get_data_with_bbox import _get_data_with_bbox2
from pynsee.geodata._get_data_with_bbox import _set_global_var
from pynsee.geodata._geojson_parser import _geojson_parser

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash


def _get_geodata(
    id, polygon=None, update=False, crs="EPSG:3857", crsPolygon="EPSG:4326"
):
    """Get geographical data with identifier and from IGN API

    Args:
        id (str): _description_
        polygon (Polygon, optional): Polygon used to constraint interested area, its crs must be EPSG:4326. Defaults to None.
        update (bool, optional): data is saved locally, set update=True to trigger an update. Defaults to False.
        crs (str, optional): CRS used for the geodata output. Defaults to 'EPSG:3857'.

    Examples:
        >>> from pynsee.geodata import get_geodata_list, get_geodata
        >>> #
        >>> # Get a list of geographical limits of French administrative areas from IGN API
        >>> geodata_list = get_geodata_list()
        >>> #
        >>> # Get geographical limits of departments
        >>> df = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')

    Returns:
        _type_: _description_
    """

    if crsPolygon not in ["EPSG:3857", "EPSG:4326"]:
        raise ValueError("crsPolygon must be either 'EPSG:3857' or 'EPSG:4326'")

    topic = "administratif"
    service = "WFS"
    Version = "2.0.0"

    # make the query link for ign
    geoportail = "https://wxs.ign.fr/{}/geoportail".format(topic)
    Service = "SERVICE=" + service + "&"
    version = "VERSION=" + Version + "&"
    request = "REQUEST=GetFeature&"
    typename = "TYPENAME=" + id + "&"
    Crs = "srsName=" + crs + "&"

    link0 = (
        geoportail
        + "/wfs?"
        + Service
        + version
        + request
        + typename
        + Crs
        + "OUTPUTFORMAT=application/json&COUNT=1000"
    )

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

        BBOX = "&BBOX={}".format(",".join(bounds))
        link = link0 + BBOX
    else:
        link = link0

    insee_folder = _create_insee_folder()
    file_name = insee_folder + "/" + _hash(link)

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        home = str(Path.home())
        user_agent = os.path.basename(home)
    except:
        user_agent = ""

    headers = {"User-Agent": "python_package_pynsee_" + user_agent.replace("/", "")}

    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["http_proxy"]}
    except:
        proxies = {"http": "", "https": ""}

    if (not os.path.exists(file_name)) | (update is True):
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        data = session.get(link, proxies=proxies, headers=headers, verify=False)

        if data.status_code == 502:
            time.sleep(1)
            data = session.get(link, proxies=proxies, headers=headers)

        if data.status_code != 200:
            print("Query:\n%s" % link)
            print(data)
            print(data.text)
            return pd.DataFrame(
                {"status": data.status_code, "comment": data.text}, index=[0]
            )

        data_json = data.json()

        json = data_json["features"]

        # if maximum reached
        # split the query with the bouding box list
        if len(json) == 1000:

            list_bbox = _get_bbox_list(
                polygon=polygon, update=update, crsPolygon=crsPolygon
            )

            Nprocesses = min(6, multiprocessing.cpu_count())

            args = [link0, list_bbox, crsPolygon]
            irange = range(len(list_bbox))

            with multiprocessing.Pool(
                initializer=_set_global_var, initargs=(args,), processes=Nprocesses
            ) as pool:

                list_data = list(
                    tqdm.tqdm(
                        pool.imap(_get_data_with_bbox2, irange), total=len(list_bbox)
                    )
                )

            data_all = pd.concat(list_data).reset_index(drop=True)

        elif len(json) != 0:

            data_all = _geojson_parser(json).reset_index(drop=True)

        else:
            msg = "!!! Query is correct but no data found !!!"
            print(msg)
            print("Query:\n%s" % link)
            if polygon is not None:
                print(
                    "!!! Check that crsPolygon argument corresponds to polygon data  !!!"
                )

            return pd.DataFrame({"status": 200, "comment": msg}, index=[0])

        # drop duplicates
        data_col = data_all.columns

        if "geometry" in data_col:

            selected_col = [col for col in data_col if col not in ["geometry", "bbox"]]
            data_all_clean = data_all[selected_col].drop_duplicates()

            row_selected = [int(i) for i in data_all_clean.index]
            geom = data_all.loc[row_selected, "geometry"]
            data_all_clean["geometry"] = geom

            if "bbox" in data_col:
                geom = data_all.loc[row_selected, "bbox"]
                data_all_clean["bbox"] = geom

            data_all_clean = data_all_clean.reset_index(drop=True)

        else:
            data_all_clean = data_all.drop_duplicates()

        # drop data outside polygon
        if polygon is not None:

            print(
                "Further checks from the user are needed as results obtained using polygon argument can be imprecise"
            )

            row_selected = []
            for i in range(len(data_all_clean)):
                geom = data_all_clean.loc[i, "geometry"]
                if geom.intersects(polygon):
                    row_selected.append(i)
            if len(row_selected) > 0:
                data_all_clean = data_all_clean.loc[row_selected, :]

        data_all_clean = data_all_clean.reset_index(drop=True)

        data_all_clean.to_pickle(file_name)
        print("Data saved: {}".format(file_name))
    else:
        try:
            data_all_clean = pd.read_pickle(file_name)
        except:
            os.remove(file_name)
            data_all_clean = _get_geodata(
                id=id, polygon=polygon, crsPolygon=crsPolygon, crs=crs, update=True
            )
        else:
            _warning_cached_data(file_name)

    data_all_clean["crs"] = crs

    return data_all_clean
