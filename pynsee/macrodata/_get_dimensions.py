# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import io
import xml.etree.ElementTree as ET

import pandas as pd

from ..utils.requests_session import PynseeAPISession
from ..utils.save_df import save_df


@save_df(day_lapse_max=90)
def _get_dataset_dimension(
    dataset, update=False, silent=False, insee_date_test=None
):
    """
    Get the variables in the dataset and the correspondance between their
    local and "key" names
    """
    INSEE_sdmx_link_datastructure = (
        "https://bdm.insee.fr/series/sdmx/datastructure/FR1"
    )
    INSEE_api_link_datastructure = (
        "https://api.insee.fr/series/BDM/V1/datastructure/FR1"
    )

    INSEE_sdmx_link_datastructure_dataset = (
        INSEE_sdmx_link_datastructure + "/" + dataset
    )
    INSEE_api_link_datastructure_dataset = (
        INSEE_api_link_datastructure + "/" + dataset
    )

    with PynseeAPISession() as session:
        results = session.request_insee(
            sdmx_url=INSEE_sdmx_link_datastructure_dataset,
            api_url=INSEE_api_link_datastructure_dataset,
        )

    dataset_dimension_file = io.BytesIO(results.content)

    root = ET.parse(dataset_dimension_file).getroot()

    data = root[1][0][0][2][0]

    n_dimension = len(data)

    list_dimension = []

    for i in range(0, n_dimension):
        dimension_id = _extract_id(data, i)
        local_rep = _extract_local_rep(data, i)

        dimension_df = {
            "dataset": dataset,
            "dimension": dimension_id,
            "local_representation": local_rep,
        }

        list_dimension.append(dimension_df)

    dimension_df_all = pd.DataFrame(list_dimension)
    dimension_df_all = dimension_df_all.dropna()

    return dimension_df_all


@save_df(day_lapse_max=90)
def _get_dimension_values(
    cl_dimension, update=False, silent=False, insee_date_test=None
):

    INSEE_sdmx_link_codelist = "https://bdm.insee.fr/series/sdmx/codelist/FR1"
    INSEE_api_link_codelist = "https://api.insee.fr/series/BDM/V1/codelist/FR1"

    INSEE_sdmx_link_codelist_dimension = (
        INSEE_sdmx_link_codelist + "/" + cl_dimension
    )
    INSEE_api_link_codelist_dimension = (
        INSEE_api_link_codelist + "/" + cl_dimension
    )

    with PynseeAPISession() as session:
        results = session.request_insee(
            sdmx_url=INSEE_sdmx_link_codelist_dimension,
            api_url=INSEE_api_link_codelist_dimension,
        )

    dimension_file = io.BytesIO(results.content)

    root = ET.parse(dimension_file).getroot()[1][0]

    list_values = []

    val_id = _extract_id(root, 0)
    name_fr = _extract_name_fr(root, 0)
    name_en = _extract_name_en(root, 0)

    dataset = {"id": [val_id], "name_fr": [name_fr], "name_en": [name_en]}

    dt = pd.DataFrame(dataset, columns=["id", "name_fr", "name_en"])

    list_values.append(dt)

    data = root[0]

    n_values = len(data)

    for i in range(2, n_values):
        val_id = _extract_id(data, i)
        name_fr = _extract_name_fr(data, i)
        name_en = _extract_name_en(data, i)

        dataset = {"id": [val_id], "name_fr": [name_fr], "name_en": [name_en]}

        dt = pd.DataFrame(dataset, columns=["id", "name_fr", "name_en"])

        list_values.append(dt)

    df_dimension_values = pd.concat(list_values)

    return df_dimension_values


def _extract_local_rep(data, i):
    try:
        local_rep = next(iter(data[i][1][0][0].attrib.values()))
    except Exception:
        local_rep = None

    return local_rep


def _extract_id(data, i):
    try:
        id_val = next(iter(data[i].attrib.values()))
    except Exception:
        id_val = None

    return id_val


def _extract_name_fr(data, i):
    try:
        name_fr = data[i][0].text
    except Exception:
        name_fr = None

    return name_fr


def _extract_name_en(data, i):
    try:
        name_en = data[i][1].text
    except Exception:
        name_en = None

    return name_en
