# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils._paste import _paste
from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def get_area_list(
    area=None, date=None, update=False, silent=False
) -> pd.DataFrame:
    """Get an exhaustive list of administrative areas : communes, departments, and urban, employment or functional areas

    Args:
        area (str, optional): Defaults to None, then get all values

        date (str): date of validity (AAAA-MM-DD)

        update (bool): locally saved data is used by default. Trigger an update with update=True.

        silent (bool, optional): Set to True, to disable messages printed in log info

    Raises:
        ValueError: Error if area is not available

    Examples:
        >>> from pynsee.localdata import get_area_list
        >>> area_list = get_area_list()
        >>> #
        >>> # get list of all communes in France
        >>> reg = get_area_list(area='regions')
    """

    list_available_area = [
        "departements",
        "regions",
        "communes",
        "communesAssociees",
        "communesDeleguees",
        "arrondissementsMunicipaux",
        "arrondissements",
        "zonesDEmploi2020",
        "airesDAttractionDesVilles2020",
        "unitesUrbaines2020",
        "collectivitesDOutreMer",
    ]
    area_string = _paste(list_available_area, collapse=" ")

    list_ZE20 = ["ZE2020", "zonesDEmploi2020", "ZoneDEmploi2020"]
    list_AAV20 = [
        "AAV2020",
        "airesDAttractionDesVilles2020",
        "AireDAttractionDesVilles2020",
    ]
    list_UU20 = ["UU2020", "unitesUrbaines2020", "UniteUrbaine2020"]

    list_ZE20 = list_ZE20 + [s.lower() for s in list_ZE20]
    list_AAV20 = list_AAV20 + [s.lower() for s in list_AAV20]
    list_UU20 = list_UU20 + [s.lower() for s in list_UU20]

    if area is not None:
        if area in list_ZE20:
            area = "zonesDEmploi2020"
        if area in list_AAV20:
            area = "airesDAttractionDesVilles2020"
        if area in list_UU20:
            area = "unitesUrbaines2020"

        if area not in list_available_area + [
            x.lower() for x in list_available_area
        ]:
            msg = (
                f"!!! {area} is not available\n"
                f"Please choose area among:\n{area_string}"
            )
            raise ValueError(msg)

        list_available_area = [area]

    list_data = []

    with PynseeAPISession() as session:

        for a in list_available_area:
            api_url = "https://api.insee.fr/metadonnees/geo/" + a
            if date:
                api_url += f"?date={date}"

            request = session.request_insee(
                api_url=api_url, file_format="application/json"
            )

            data = request.json()
            list_data += data

    data_all = pd.DataFrame(list_data)

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
