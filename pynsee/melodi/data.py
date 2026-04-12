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
    id_dataset, language: str = "all", raise_if_not_ok: bool = True, **filters
) -> pd.DataFrame:
    """
    Get a MELODI dataset (pagination is handled by pynsee if need be).

    Note: as pagination is handled, `page`, `maxResult` and `totalCount`
    arguments should NOT be added to the kwargs and will be ignored. `range`
    will also be ignored : to retrieve a dataset's dimensions, have a look at
    `pynsee.melodi.get_range`.

    Parameters
    ----------
    id_dataset : str
        Dataset's identifier.
    language : str, optional
        If set to "all", will keep metadata's labels in every available language.
        Can be used to keep only one desired language label (API covered
        languages include either "en" of "fr"). The default is "all".
    raise_if_not_ok : bool, optional
        If set to True, a RequestException will automatically be raised if
        the response is not ok (= `status_code` < 400).
        The default is True.
    **filters :
        Optional filters to be used on MELODI. To get the available filters,
        please look at `pynsee.melodi.get_range`. Note that even if MELODI's
        filters' labels are UPPERCASE, pynsee handles lowercase in consistence
        with python's conventions.

    Raises
    ------
    RequestException
        If the JSON cannot be parsed.
    ValueError
        If the result after pagination is incoherent with the estimated
        results' shape. This should NOT happen and is triggered to warn users
        to get in touch if this arises.

    Returns
    -------
    observations : pd.DataFrame
        Dataset's as a DataFrame.

    Examples
    -------
    >>> get_melodi_dataset("DS_TICM_PRATIQUES")

    #           TICM_MEASURE SEX FREQ EMPSTA TIME_PERIOD   EDUC PCS_ESE     AGE  \
    # 0               PROFIL  _T    A     _T        2022     _T      _T  Y60T74
    # 1          TEL_PAR_INT   F    A     _T        2023     _T      _T  Y_GE60
    # 2    WEB_12MOIS_X_EGOV   F    A     _T        2015     _T      _T  Y_GE60
    # 3              LECTURE  _T    A     _T        2012  2_353      _T  Y15T44
    # 4            WEB_3MOIS   F    A     _T        2025     _T      _T  Y45T59
    # ..                 ...  ..  ...    ...         ...    ...     ...     ...
    # 331        VENTE_3MOIS  _T    A     _T        2010    4T8      _T  Y45T59
    # 332  WEB_12MOIS_X_EGOV  _T    A     _T        2009    0T1      _T  Y15T44
    # 333      NO_WEB_12MOIS   M    A     _T        2015     _T      _T  Y_GE60
    # 334            LECTURE  _T    A     _T        2018    0T1      _T  Y15T44
    # 335          WEB_3MOIS  _T    A     _T        2013  2_353      _T  Y15T44

    #     OBS_STATUS  OBS_VALUE_NIVEAU                     title_en  \
    # 0            A              19.4  Internet use of individuals
    # 1            A              38.6  Internet use of individuals
    # 2            L               NaN  Internet use of individuals
    # 3            L               NaN  Internet use of individuals
    # 4            A              96.4  Internet use of individuals
    # ..         ...               ...                          ...
    # 331          L               NaN  Internet use of individuals
    # 332          L               NaN  Internet use of individuals
    # 333          L               NaN  Internet use of individuals
    # 334          L               NaN  Internet use of individuals
    # 335          A              93.9  Internet use of individuals

    #                               title_fr         identifier publisher_id  \
    # 0    Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 1    Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 2    Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 3    Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 4    Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # ..                                 ...                ...          ...
    # 331  Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 332  Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 333  Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 334  Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE
    # 335  Pratiques en ligne des personnes   DS_TICM_PRATIQUES        INSEE

    #                                           publisher_fr  \
    # 0    Institut national de la statistique et des etu...
    # 1    Institut national de la statistique et des etu...
    # 2    Institut national de la statistique et des etu...
    # 3    Institut national de la statistique et des etu...
    # 4    Institut national de la statistique et des etu...
    # ..                                                 ...
    # 331  Institut national de la statistique et des etu...
    # 332  Institut national de la statistique et des etu...
    # 333  Institut national de la statistique et des etu...
    # 334  Institut national de la statistique et des etu...
    # 335  Institut national de la statistique et des etu...

    #                                           publisher_en
    # 0    National Institute of Statistics and Economic ...
    # 1    National Institute of Statistics and Economic ...
    # 2    National Institute of Statistics and Economic ...
    # 3    National Institute of Statistics and Economic ...
    # 4    National Institute of Statistics and Economic ...
    # ..                                                 ...
    # 331  National Institute of Statistics and Economic ...
    # 332  National Institute of Statistics and Economic ...
    # 333  National Institute of Statistics and Economic ...
    # 334  National Institute of Statistics and Economic ...
    # 335  National Institute of Statistics and Economic ...

    # [10336 rows x 16 columns]

    >>> get_melodi_dataset("DS_TICM_PRATIQUES", language="fr").head(2)

    #   TICM_MEASURE SEX FREQ EMPSTA TIME_PERIOD EDUC PCS_ESE     AGE OBS_STATUS  \
    # 0       PROFIL  _T    A     _T        2022   _T      _T  Y60T74          A
    # 1  TEL_PAR_INT   F    A     _T        2023   _T      _T  Y_GE60          A

    #    OBS_VALUE_NIVEAU                           title_fr         identifier  \
    # 0              19.4  Pratiques en ligne des personnes   DS_TICM_PRATIQUES
    # 1              38.6  Pratiques en ligne des personnes   DS_TICM_PRATIQUES

    #   publisher_id                                       publisher_fr
    # 0        INSEE  Institut national de la statistique et des etu...
    # 1        INSEE  Institut national de la statistique et des etu...

    >>> get_melodi_dataset(
        "DS_TICM_PRATIQUES",
        language="fr",
        time_period=2025,
        sex="F",
        age="Y45T59"
        )

    #          TICM_MEASURE SEX FREQ EMPSTA TIME_PERIOD EDUC PCS_ESE     AGE  \
    # 0           WEB_3MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 1         RESEAUX_SOC   F    A     _T        2025   _T      _T  Y45T59
    # 2          ACHA_3MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 3   WEB_12MOIS_X_EGOV   F    A     _T        2025   _T      _T  Y45T59
    # 4     COMPTE_BANCAIRE   F    A     _T        2025   _T      _T  Y45T59
    # 5         ACHA_12MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 6         EGOV_12MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 7         TEL_PAR_INT   F    A     _T        2025   _T      _T  Y45T59
    # 8         VENTE_3MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 9       NO_WEB_12MOIS   F    A     _T        2025   _T      _T  Y45T59
    # 10              EMAIL   F    A     _T        2025   _T      _T  Y45T59
    # 11            LECTURE   F    A     _T        2025   _T      _T  Y45T59
    # 12             PROFIL   F    A     _T        2025   _T      _T  Y45T59
    # 13          QUOTIDIEN   F    A     _T        2025   _T      _T  Y45T59
    # 14      INFO_PRODUITS   F    A     _T        2025   _T      _T  Y45T59
    # 15            NO_EGOV   F    A     _T        2025   _T      _T  Y45T59

    #    OBS_STATUS  OBS_VALUE_NIVEAU                           title_fr  \
    # 0           A              96.4  Pratiques en ligne des personnes
    # 1           A              71.5  Pratiques en ligne des personnes
    # 2           A              71.6  Pratiques en ligne des personnes
    # 3           A               5.1  Pratiques en ligne des personnes
    # 4           A              80.0  Pratiques en ligne des personnes
    # 5           A              83.2  Pratiques en ligne des personnes
    # 6           A              92.1  Pratiques en ligne des personnes
    # 7           A              75.1  Pratiques en ligne des personnes
    # 8           A              25.7  Pratiques en ligne des personnes
    # 9           A               2.9  Pratiques en ligne des personnes
    # 10          A              92.2  Pratiques en ligne des personnes
    # 11          A              54.8  Pratiques en ligne des personnes
    # 12          L               NaN  Pratiques en ligne des personnes
    # 13          A              91.1  Pratiques en ligne des personnes
    # 14          A              70.2  Pratiques en ligne des personnes
    # 15          A               7.9  Pratiques en ligne des personnes

    #            identifier publisher_id  \
    # 0   DS_TICM_PRATIQUES        INSEE
    # 1   DS_TICM_PRATIQUES        INSEE
    # 2   DS_TICM_PRATIQUES        INSEE
    # 3   DS_TICM_PRATIQUES        INSEE
    # 4   DS_TICM_PRATIQUES        INSEE
    # 5   DS_TICM_PRATIQUES        INSEE
    # 6   DS_TICM_PRATIQUES        INSEE
    # 7   DS_TICM_PRATIQUES        INSEE
    # 8   DS_TICM_PRATIQUES        INSEE
    # 9   DS_TICM_PRATIQUES        INSEE
    # 10  DS_TICM_PRATIQUES        INSEE
    # 11  DS_TICM_PRATIQUES        INSEE
    # 12  DS_TICM_PRATIQUES        INSEE
    # 13  DS_TICM_PRATIQUES        INSEE
    # 14  DS_TICM_PRATIQUES        INSEE
    # 15  DS_TICM_PRATIQUES        INSEE

    #                                          publisher_fr
    # 0   Institut national de la statistique et des etu...
    # 1   Institut national de la statistique et des etu...
    # 2   Institut national de la statistique et des etu...
    # 3   Institut national de la statistique et des etu...
    # 4   Institut national de la statistique et des etu...
    # 5   Institut national de la statistique et des etu...
    # 6   Institut national de la statistique et des etu...
    # 7   Institut national de la statistique et des etu...
    # 8   Institut national de la statistique et des etu...
    # 9   Institut national de la statistique et des etu...
    # 10  Institut national de la statistique et des etu...
    # 11  Institut national de la statistique et des etu...
    # 12  Institut national de la statistique et des etu...
    # 13  Institut national de la statistique et des etu...
    # 14  Institut national de la statistique et des etu...
    # 15  Institut national de la statistique et des etu...

    """

    url = f"https://api.insee.fr/melodi/data/{id_dataset}"

    # set to uppercase if need be
    filters = {k.upper(): v for k, v in filters.items()}

    params = filters.copy()
    params["totalCount"] = True
    # params["range"] = True

    params["maxResult"] = 0
    params["page"] = 1

    if params:
        url_api_count = f"{url}?{urlencode(params)}"
        del params["maxResult"]
        url_api = f"{url}?{urlencode(params)}"

    observations = []

    with PynseeAPISession() as session:

        # check iterations count
        r = session.request_insee(
            url_api_count,
            file_format="application/json",
            raise_if_not_ok=raise_if_not_ok,
        )

        # parse metadata only once to reduce RAM consumption
        metadata = _parse_metadata(r, language=language)

        count = r.json()["paging"]["count"]
        count_pages = count // SIZE + (0 if count % SIZE == 0 else 1)

        # download
        data = {"paging": {"next": url_api}}
        for x in tqdm(range(count_pages), desc="Downloading"):
            url = data["paging"]["next"]
            r = session.request_insee(
                url,
                file_format="application/json",
                raise_if_not_ok=raise_if_not_ok,
            )
            try:
                data = r.json()
            except requests.exceptions.JSONDecodeError as e:
                raise requests.exceptions.RequestException(
                    f"an error occured on {url}"
                ) from e

            observations.append(_parse_dataset_observations(r))

        if not data["paging"].get("isLast", True):
            raise ValueError(
                "An unexpected error occured, please get in touch"
            )

    observations = pd.concat(observations, ignore_index=True).assign(
        **metadata
    )
    if len(observations) != count:
        raise ValueError("An unexpected error occured, please get in touch")

    return observations


@save_df(day_lapse_max=90)
def get_range(
    id_dataset: str,
    language: str = "all",
    include_values: bool = False,
    raise_if_not_ok: bool = True,
) -> pd.DataFrame:
    """
    Get a dataset's available dimensions (ie "ranges").

    Available dimensions can be retrieved in a sparse format (with only
    the dimensions' descriptions) or a long format (including all available
    values for each dimension).

    Parameters
    ----------
    id_dataset : str
        Dataset's identifier.
    language : str, optional
        If set to "all", will keep metadata's labels in every available language.
        Can be used to keep only one desired language label (API covered
        languages include either "en" of "fr"). The default is "all".
    include_values : bool, optional
        Whether to include each available value for each dimension. The default
        is False, resulting to the sparse format. Set to True to get the long
        format dataframe.
    raise_if_not_ok : bool, optional
        If set to True, a RequestException will automatically be raised if
        the response is not ok (= `status_code` < 400).
        The default is True.

    Returns
    -------
    ranges : pd.DataFrame
        DataFrame describing the available ranges.

    Examples
    -------
    >>> get_range("DS_RP_POPULATION_PRINC")

    #   concept_code      concept_en              concept_fr       type
    # 0          GEO       Geography              Géographie        geo
    # 1          SEX             Sex                    Sexe  modalites
    # 2  TIME_PERIOD     Time period      Période temporelle       date
    # 3   RP_MEASURE  Census measure  Mesure du recensement   modalites
    # 4          AGE             Age                     Âge  modalites
    # 5      MEASURE         Measure                  Mesure    mesures

    >>> get_range("DS_RP_POPULATION_PRINC", language="fr")

    #   concept_code              concept_fr       type
    # 0          GEO              Géographie        geo
    # 1          SEX                    Sexe  modalites
    # 2  TIME_PERIOD      Période temporelle       date
    # 3   RP_MEASURE  Mesure du recensement   modalites
    # 4          AGE                     Âge  modalites
    # 5      MEASURE                  Mesure    mesures

    >>> get_range("DS_RP_POPULATION_PRINC", language="fr", include_values=True)

    #       concept_code  concept_fr       type              code  \
    # 0              GEO  Géographie        geo         200000172
    # 1              GEO  Géographie        geo         200000438
    # 2              GEO  Géographie        geo         200000545
    # 3              GEO  Géographie        geo         200000628
    # 4              GEO  Géographie        geo         200000800
    #            ...         ...        ...               ...
    # 41778          AGE         Âge  modalites            Y_GE80
    # 41779          AGE         Âge  modalites            Y_LT15
    # 41780          AGE         Âge  modalites            Y_LT20
    # 41781          AGE         Âge  modalites                _T
    # 41782      MEASURE      Mesure    mesures  OBS_VALUE_NIVEAU

    #                         id                                                iri  \
    # 0      2025-EPCI-200000172  http://id.insee.fr/geo/intercommunalite/f276d0...
    # 1      2025-EPCI-200000438  http://id.insee.fr/geo/intercommunalite/fa17bc...
    # 2      2025-EPCI-200000545  http://id.insee.fr/geo/intercommunalite/2afe50...
    # 3      2025-EPCI-200000628  http://id.insee.fr/geo/intercommunalite/69572d...
    # 4      2025-EPCI-200000800  http://id.insee.fr/geo/intercommunalite/934906...
    #                    ...                                                ...
    # 41778                  NaN                                                NaN
    # 41779                  NaN                                                NaN
    # 41780                  NaN                                                NaN
    # 41781                  NaN                                                NaN
    # 41782                  NaN                                                NaN

    #                                                 value_fr type_code  \
    # 0                Communauté de communes Faucigny-Glières      EPCI
    # 1      Communauté de communes du Pays de Pontchâteau ...      EPCI
    # 2      Communauté de communes des Portes de Romilly-s...      EPCI
    # 3              Communauté de communes Rhône Lez Provence      EPCI
    # 4                 Communauté de communes Cœur de Sologne      EPCI
    #                                                  ...       ...
    # 41778                                     80 ans ou plus       NaN
    # 41779                                    Moins de 15 ans       NaN
    # 41780                                    Moins de 20 ans       NaN
    # 41781                                              Total       NaN
    # 41782                                             Valeur       NaN

    #                                                  type_fr measure_type_code  \
    # 0      Etablissement public de coopération intercommunal               NaN
    # 1      Etablissement public de coopération intercommunal               NaN
    # 2      Etablissement public de coopération intercommunal               NaN
    # 3      Etablissement public de coopération intercommunal               NaN
    # 4      Etablissement public de coopération intercommunal               NaN
    #                                                  ...               ...
    # 41778                                                NaN               NaN
    # 41779                                                NaN               NaN
    # 41780                                                NaN               NaN
    # 41781                                                NaN               NaN
    # 41782                                                NaN            NIVEAU

    #       measure_type_id  measure_type_ordreRmes measure_type_total  \
    # 0                 NaN                     NaN                NaN
    # 1                 NaN                     NaN                NaN
    # 2                 NaN                     NaN                NaN
    # 3                 NaN                     NaN                NaN
    # 4                 NaN                     NaN                NaN
    #               ...                     ...                ...
    # 41778             NaN                     NaN                NaN
    # 41779             NaN                     NaN                NaN
    # 41780             NaN                     NaN                NaN
    # 41781             NaN                     NaN                NaN
    # 41782          NIVEAU                     1.0              False

    #       measure_type_uri measure_type_fr
    # 0                  NaN             NaN
    # 1                  NaN             NaN
    # 2                  NaN             NaN
    # 3                  NaN             NaN
    # 4                  NaN             NaN
    #                ...             ...
    # 41778              NaN             NaN
    # 41779              NaN             NaN
    # 41780              NaN             NaN
    # 41781              NaN             NaN
    # 41782           NIVEAU          Niveau

    # [41783 rows x 15 columns]


    """

    url = f"https://api.insee.fr/melodi/range/{id_dataset}"

    with PynseeAPISession() as session:
        r = session.request_insee(
            url,
            file_format="application/json",
            raise_if_not_ok=raise_if_not_ok,
        )

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
        ranges = concepts.join(values).drop_duplicates().reset_index(drop=True)

    else:
        ranges = concepts

    return ranges


if __name__ == "__main__":
    # from pynsee.melodi import get_melodi_catalog

    # print(get_range("DS_RP_POPULATION_PRINC"))

    df = get_melodi_dataset("DS_TICM_PRATIQUES")

    # df = get_melodi_dataset(
    #     "DS_RP_POPULATION_PRINC", "all", GEO="2025-EPCI-200000172"
    # )

    # cat = get_melodi_catalog()
    # for identifier in tqdm(cat["dataset_identifier"].drop_duplicates()):
    #     get_range(identifier, include_values=True)

    # test = get_melodi_dataset("DS_TICM_PRATIQUES")
    # test = get_range("DS_RP_POPULATION_PRINC", include_values=True)
    # test = get_range("DS_TICM_PRATIQUES", include_values=True)
    # print(test)
