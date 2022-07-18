# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import xml.etree.ElementTree as ET
import pandas as pd
import os
import re
import datetime

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._get_temp_dir import _get_temp_dir


@lru_cache(maxsize=None)
def get_last_release():
    """Get the datasets from BDM macroeconomic database released in the last 30 days

    Examples
        >>> from pynsee.macrodata import get_last_release
        >>> dataset_released = get_last_release()
    """
    link = "https://bdm.insee.fr/series/sdmx/rss/donnees"

    request = _request_insee(sdmx_url=link)

    file = _get_temp_dir() + "\\last_release"

    with open(file, "wb") as f:
        f.write(request.content)

    root = ET.parse(file).getroot()

    if os.path.exists(file):
        os.remove(file)

    list_data = []

    for i in range(len(root[0])):
        if root[0][i].tag == "item":
            dico = {}

            for j in range(len(root[0][i])):
                if root[0][i][j].tag == "pubDate":
                    date = datetime.datetime.strptime(
                        root[0][i][j].text, "%a, %d %b %Y %H:%M:%S GMT"
                    )
                    dico["pubDate"] = date
                else:
                    dico[root[0][i][j].tag] = root[0][i][j].text

                if root[0][i][j].tag == "title":
                    string = re.search("\\[.*\\]", root[0][i][j].text)
                    if string:
                        string_selected = (
                            string.group(0).replace("[", "").replace("]", "")
                        )
                    else:
                        string_selected = string
                    dico["dataset"] = string_selected

            df = pd.DataFrame(dico, index=[0])
            list_data.append(df)

    data = pd.concat(list_data)

    return data
