# -*- coding: utf-8 -*-
"""
#TODO

// Note: available functions in R package :
    get_catalog
    get_all_data
    get_data
    get_file
    get_local_data
    get_local_data_by_com
    get_metadata
    get_range
    get_range_geo

    https://github.com/InseeFrLab/melodi/tree/main/R

"""

import logging
from urllib.parse import urlencode

import pandas as pd
import requests
from tqdm import tqdm

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df

SIZE = 10_000

logger = logging.getLogger(__name__)


def _parse_metadata(
    response: requests.Response, language: str = "all"
) -> dict:

    data = response.json()

    metadata = {}
    for lang, title in data["title"].items():
        if language in {"all", lang}:
            metadata[f"title_{lang}"] = title

    metadata["identifier"] = data["identifier"]

    metadata["publisher_id"] = data["publisher"]["id"]
    for d in data["publisher"]["label"]:
        if isinstance(d, dict) and all(
            j in d.keys() for j in ["lang", "content"]
        ):
            if language in {"all", d["lang"]}:
                metadata["publisher_" + d["lang"]] = d["content"]

    return metadata


def _parse_dataset_observations(response: requests.Response):

    data = response.json()

    obs = pd.DataFrame(data["observations"])
    for f in "dimensions", "attributes":
        if f in obs.columns:
            obs = obs.drop(f, axis=1).join(
                pd.DataFrame(obs[f].values.tolist())
            )

    if "measures" in obs.columns:
        measures = obs.measures.str["OBS_VALUE_NIVEAU"].str["value"]
        obs["OBS_VALUE_NIVEAU"] = measures
        obs = obs.drop("measures", axis=1)

    return obs


@save_df(day_lapse_max=90)
def get_melodi_dataset(
    id_dataset, language="all", page=1, **filters
) -> pd.DataFrame:

    url = f"https://api.insee.fr/melodi/data/{id_dataset}"

    params = filters.copy()
    params["totalCount"] = True
    # params["range"] = True

    params["maxResult"] = 0
    params["page"] = page

    if params:
        url_api_count = f"{url}?{urlencode(params)}"
        del params["maxResult"]
        url_api = f"{url}?{urlencode(params)}"

    observations = []

    with PynseeAPISession() as session:

        # check iterations count
        r = session.request_insee(
            url_api_count, file_format="application/json"
        )

        # parse metadata only once to reduce RAM consumption
        metadata = _parse_metadata(r, language=language)

        count = r.json()["paging"]["count"]
        count_pages = count // SIZE + (0 if count % SIZE == 0 else 1)

        # download
        data = {"paging": {"next": url_api}}
        for x in tqdm(range(count_pages), desc="Downloading"):
            url = data["paging"]["next"]
            r = session.request_insee(url, file_format="application/json")
            try:
                data = r.json()
            except requests.exceptions.JSONDecodeError as e:
                raise requests.exceptions.RequestException(
                    f"an error occured on {url}"
                ) from e

            observations.append(_parse_dataset_observations(r))

        if not data["paging"]["isLast"]:
            raise ValueError(
                "An unexpected error occured, please get in touch"
            )

    observations = pd.concat(observations).assign(**metadata)
    if len(observations) != count:
        raise ValueError("An unexpected error occured, please get in touch")

    return observations


@save_df(day_lapse_max=90)
def get_range(id_dataset, language="all", include_values=False):

    url = f"https://api.insee.fr/melodi/range/{id_dataset}"

    with PynseeAPISession() as session:
        r = session.request_insee(url, file_format="application/json")

    ranges = r.json()["range"]

    ranges = pd.DataFrame(ranges)

    concepts = (
        ranges["concept"]
        .str["code"]
        .to_frame("concept_code")
        .join(pd.DataFrame(ranges["concept"].str["label"].values.tolist()))
    )
    languages = [
        x
        for x in concepts.columns.tolist()
        if "_" not in x and (language == "all" or x == language)
    ]

    concepts = (
        concepts[["concept_code"] + languages]
        .rename(columns={x: f"concept_{x}" for x in languages})
        .join(ranges["type"])
    )

    if include_values:
        values = ranges.explode("values", ignore_index=False)["values"]
        values = values.to_frame().reset_index(drop=False)

        values = pd.DataFrame(
            values["values"].tolist(), index=values.index
        ).join(values["index"])

        labels = pd.DataFrame(values["label"].tolist())

        values = (
            values.drop("label", axis=1)
            .join(labels[languages])
            .rename(
                columns={
                    x: f"value_{x}"
                    for x in languages
                    if x in set(labels.columns)
                }
            )
        )

        if "type" in values.columns:
            ix = values[~values.type.isnull()].index
            types = pd.DataFrame(
                values.loc[ix, "type"].values.tolist(), index=ix
            )[["code"] + languages]
            types = types.rename(
                columns={x: f"type_{x}" for x in types.columns}
            )

            values = values.drop("type", axis=1).join(types)

        if "measureType" in values.columns:
            ix = values[~values.measureType.isnull()].index
            measure_types = pd.DataFrame(
                values.loc[ix, "measureType"].values.tolist(), index=ix
            )  # [["code"] + languages]
            labels = pd.DataFrame(
                measure_types["libelle"].tolist(), index=labels.index
            )[languages]
            labels = labels.rename(
                columns={x: f"measure_type_{x}" for x in labels.columns},
            )

            measure_types = measure_types.drop("libelle", axis=1)
            measure_types = measure_types.rename(
                columns={x: f"measure_type_{x}" for x in measure_types.columns}
            ).join(labels)

            values = values.drop("measureType", axis=1).join(measure_types)

        values = values.set_index("index")
        concepts = concepts.join(values)
    return concepts


if __name__ == "__main__":

    # test = get_melodi_dataset("DS_TICM_PRATIQUES")
    # test = get_range("DS_RP_POPULATION_PRINC", include_values=True)
    test = get_range("DS_TICM_PRATIQUES", include_values=True)
    print(test)
