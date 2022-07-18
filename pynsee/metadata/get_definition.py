# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.utils._request_insee import _request_insee
from tqdm import trange

import re
import pandas as pd


def get_definition(ids):
    """Get the definition of a concept from its identifier

    Args:
        ids (list): a list of concept identifiers

    Raises:
        ValueError: an error is raised if ids is not a list

    Examples:
        >>> from pynsee.metadata import get_definition_list, get_definition
        >>> def_list = get_definition_list()
        >>> # geographic areas definition
        >>> geo_definitions = get_definition(['c1468', 'c1282', 'c1762',
        >>>                       'c1501', 'c1346', 'c1502', 'c1912',
        >>>                       'c1361', 'c2173', 'c2070'])

    """
    if type(ids) == str:
        ids = [ids]

    if type(ids) != list:
        raise ValueError("!!! ids must be a list or a str!!!")

    # ids = ['c1020', 'c1601']

    link = "https://api.insee.fr/metadonnees/V1/concepts/definition"

    list_data = []

    def clean_definition(string):
        m = re.search("\\<p\\>.*\\<\\/p\\>", string)
        if m:
            string_selected = m.group(0)
            string_cleaned = (
                string_selected.replace("<p>", "")
                .replace("</p>", "")
                .replace("\xa0", " ")
            )
        else:
            string_cleaned = string
        return string_cleaned

    def extract_data(data, item1, i, item2):
        try:
            val = data[item1][i][item2]
        except:
            val = None
        return val

    for i in trange(len(ids), desc="Getting data"):

        id = ids[i]
        query = link + "/" + id

        request = _request_insee(api_url=query, file_format="application/json")

        try:
            data = request.json()

            title_fr = None
            title_en = None

            if data["intitule"][0]["langue"] == "fr":
                title_fr = extract_data(data, item1="intitule", i=0, item2="contenu")
                title_en = extract_data(data, item1="intitule", i=1, item2="contenu")

            def_fr = None
            def_en = None

            if data["definition"][0]["langue"] == "fr":
                def_fr = extract_data(data, item1="definition", i=0, item2="contenu")
                def_en = extract_data(data, item1="definition", i=1, item2="contenu")
                def_fr = clean_definition(def_fr)
                def_en = clean_definition(def_en)

            def_short_fr = None
            def_short_en = None

            try:
                if data["definitionCourte"][0]["langue"] == "fr":
                    def_short_fr = extract_data(
                        data, item1="definitionCourte", i=0, item2="contenu"
                    )
                    def_short_en = extract_data(
                        data, item1="definitionCourte", i=1, item2="contenu"
                    )
                    def_short_fr = clean_definition(def_short_fr)
                    def_short_en = clean_definition(def_short_en)
            except:
                pass

            update = data["dateMiseAJour"]

            uri = data["uri"]

            df = pd.DataFrame(
                {
                    "ID": id,
                    "TITLE_FR": title_fr,
                    "TITLE_EN": title_en,
                    "DEFINITION_SHORT_FR": def_short_fr,
                    "DEFINITION_SHORT_EN": def_short_en,
                    "DEFINITION_FR": def_fr,
                    "DEFINITION_EN": def_en,
                    "UPDATE": update,
                    "URI": uri,
                },
                index=[0],
            )
        except:
            df = pd.DataFrame(
                {
                    "ID": id,
                    "TITLE_FR": None,
                    "TITLE_EN": None,
                    "DEFINITION_SHORT_FR": None,
                    "DEFINITION_SHORT_EN": None,
                    "DEFINITION_FR": None,
                    "DEFINITION_EN": None,
                    "UPDATE": None,
                    "URI": None,
                },
                index=[0],
            )

        list_data.append(df)

    data_final = pd.concat(list_data)
    data_final = data_final.reset_index(drop=True)

    return data_final
