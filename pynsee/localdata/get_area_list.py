# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._paste import _paste


@lru_cache(maxsize=None)
def get_area_list(area=None):
    """Get a list of non administrative areas : urban, employment or functional areas

    Args:
        area (str, optional): Defaults to None, then get all values

    Raises:
        ValueError: Error if area is not available

    Examples:
        >>> from pynsee.localdata import get_area_list
        >>> area_list = get_area_list()
    """

    list_available_area = [
        "zonesDEmploi2020",
        "airesDAttractionDesVilles2020",
        "unitesUrbaines2020",
    ]
    area_string = _paste(list_available_area, collapse=" ")

    list_ZE20 = ["ZE2020", "zonesDEmploi2020", "ZoneDEmploi2020"]
    list_AAV20 = [
        "AAV2020",
        "airesDAttractionDesVilles2020",
        "AireDAttractionDesVilles2020",
    ]
    list_UU20 = ["UU2020", "unitesUrbaines2020", "UniteUrbaine2020"]

    list_ZE20 = [s.lower() for s in list_ZE20]
    list_AAV20 = [s.lower() for s in list_AAV20]
    list_UU20 = [s.lower() for s in list_UU20]

    if area is not None:
        area = area.lower()

        if area in list_ZE20:
            area = "zonesDEmploi2020"
        if area in list_AAV20:
            area = "airesDAttractionDesVilles2020"
        if area in list_UU20:
            area = "unitesUrbaines2020"

        if area not in list_available_area:
            msg = "!!! {} is not available\nPlease choose area among:\n{}".format(
                area, area_string
            )
            raise ValueError(msg)
        else:
            list_available_area = [area]

    list_data = []

    for a in list_available_area:
        api_url = "https://api.insee.fr/metadonnees/V1/geo/" + a + "?date=*"

        request = _request_insee(api_url=api_url, file_format="application/json")

        data = request.json()

        for i in range(len(data)):
            df = pd.DataFrame(data[i], index=[0])
            list_data.append(df)

    data_all = pd.concat(list_data).reset_index(drop=True)

    data_all.rename(
        columns={
            "code": "CODE",
            "uri": "URI",
            "dateCreation": "DATE_CREATION",
            "intituleSansArticle": "TITLE_SHORT",
            "type": "AREA_TYPE",
            "typeArticle": "DETERMINER_TYPE",
            "intitule": "TITLE",
            "dateSuppression": "DATE_DELETION",
        },
        inplace=True,
    )

    return data_all
