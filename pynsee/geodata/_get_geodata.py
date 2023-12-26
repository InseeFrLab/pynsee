# -*- coding: utf-8 -*-

import time
import pandas as pd
import requests
import os
import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path
import urllib3
import warnings
import asyncio
import nest_asyncio

from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.geodata._get_bbox_list import _get_bbox_list
#from pynsee.geodata._get_data_with_bbox import _get_data_with_bbox2
#from pynsee.geodata._get_data_with_bbox import _set_global_var
from pynsee.geodata._get_data_from_bbox_list import _get_data_from_bbox_list
from pynsee.geodata._geojson_parser import _geojson_parser

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

import logging

logger = logging.getLogger(__name__)


def _get_geodata(
    id, update=False, crs="EPSG:3857"
):
    """Get geographical data with identifier and from IGN API

    Args:
        id (str): _description_
        to None.
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

    link = link0

    insee_folder = _create_insee_folder()
    file_name = insee_folder + "/" + _hash(link)

    if (not os.path.exists(file_name)) | (update is True):
        with requests.Session() as session:
            retry = Retry(connect=3, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            try:
                home = str(Path.home())
                user_agent = os.path.basename(home)
            except Exception:
                user_agent = ""

            headers = {
                "User-Agent": "python_package_pynsee_"
                + user_agent.replace("/", "")
            }

            proxies = {}
            for key in ["http", "https"]:
                try:
                    proxies[key] = os.environ[f"{key}_proxy"]
                except KeyError:
                    proxies[key] = ""

            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore", urllib3.exceptions.InsecureRequestWarning
                )
                data = session.get(
                    link, proxies=proxies, headers=headers, verify=False
                )

                if data.status_code == 502:
                    time.sleep(1)
                    data = session.get(link, proxies=proxies, headers=headers)

                if data.status_code != 200:
                    logger.debug("Query:\n%s" % link)
                    logger.debug(data)
                    logger.debug(data.text)
                    return pd.DataFrame(
                        {"status": data.status_code, "comment": data.text},
                        index=[0],
                    )

        data_json = data.json()

        json = data_json["features"]

        # if maximum reached
        # split the query with the bouding box list
        if len(json) == 1000:
            list_bbox = _get_bbox_list(update=update)

            list_data = asyncio.run(_get_data_from_bbox_list(id, list_bbox))
            
            #try:
            #    list_data = asyncio.run(_get_data_from_bbox_list(id, list_bbox))
            #except Exception as e:
                # solution from
                # https://github.com/langchain-ai/langchain/issues/8494
                #print(e)
                #print('\n')
                #loop = asyncio.get_event_loop()
                #list_data = loop.run_until_complete(_get_data_from_bbox_list(id, list_bbox))

                #list_data = nest_asyncio.apply(_get_data_from_bbox_list(id, list_bbox))
                
                #list_data = await _get_data_from_bbox_list(id, list_bbox)
            
            list_data = [_geojson_parser(json) for json in list_data]
            
            data_all = pd.concat(list_data).reset_index(drop=True)

        elif len(json) != 0:
            data_all = _geojson_parser(json).reset_index(drop=True)

        else:
            msg = f"Query is correct but no data found : {link}"
            logger.error(msg)
            return pd.DataFrame({"status": 200, "comment": msg}, index=[0])

        # drop duplicates
        data_col = data_all.columns

        if "geometry" in data_col:
            selected_col = [
                col for col in data_col if col not in ["geometry", "bbox"]
            ]
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

        data_all_clean = data_all_clean.reset_index(drop=True)

        data_all_clean.to_pickle(file_name)
        logger.info("Data saved: {}".format(file_name))
    else:
        try:
            data_all_clean = pd.read_pickle(file_name)
        except Exception:
            os.remove(file_name)
            data_all_clean = _get_geodata(
                id=id,
                crs=crs,
                update=True,
            )
        else:
            _warning_cached_data(file_name)

    data_all_clean["crsCoord"] = crs

    return data_all_clean
