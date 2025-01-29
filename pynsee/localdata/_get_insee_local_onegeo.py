# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession


@lru_cache(maxsize=None)
def _get_insee_local_onegeo(variables, dataset_version, nivgeo, codegeo):

    count_sep = variables.count("-")
    modalite = ".all" * (count_sep + 1)

    link = "https://api.insee.fr/donnees-locales/donnees/"
    link = link + "geo-{}@{}/{}-{}{}".format(
        variables, dataset_version, nivgeo, codegeo, modalite
    )

    with PynseeAPISession() as session:
        request = session.request_insee(
            api_url=link, file_format="application/json;charset=utf-8"
        )

    data_request = request.json()

    Cellule = data_request["Cellule"]
    Variable = data_request["Variable"]
    Croisement = data_request["Croisement"]

    dataset_version = Croisement["JeuDonnees"]["code"]
    dataset_name = Croisement["JeuDonnees"]["Source"]
    data_date = Croisement["JeuDonnees"]["Annee"]

    list_data = []

    for i in range(len(Cellule)):
        dico = {**Cellule[i]["Zone"], **Cellule[i]["Mesure"]}
        modalite = Cellule[i]["Modalite"]

        for m in range(len(modalite)):
            try:
                dico_added = {modalite[m]["variable"]: modalite[m]["code"]}
            except Exception:
                dico_added = {modalite["variable"]: modalite["code"]}
            dico = {**dico, **dico_added}

        dico["OBS_VALUE"] = Cellule[i]["Valeur"]
        dico = {k: v for k, v in dico.items() if len(v) != 0}
        try:
            df = pd.DataFrame(dico, index=[0])
        except Exception:
            df = pd.DataFrame(dico)

        list_data.append(df)

    data = pd.concat(list_data)

    for i in range(len(Variable)):

        list_dict_var = []
        values = Variable[i]["Modalite"]
        for d in range(len(values)):
            df_dict = pd.DataFrame(values[d], index=[0])
            list_dict_var.append(df_dict)

        var_name = Variable[i]["code"]

        df = (
            pd.concat(list_dict_var)
            .reset_index(drop=True)
            .drop(columns=["variable"])
            .rename(columns={"code": var_name})
        )

        data[f"{var_name}_label"] = Variable[i]["Libelle"]

        data = data.merge(df, on=var_name, how="left")
    data = data.assign(
        DATASET_VERSION=dataset_version,
        DATASET_NAME=dataset_name,
        DATA_DATE=data_date,
    )

    data.rename(
        columns={
            "codgeo": "CODEGEO",
            "nivgeo": "NIVGEO",
            "code": "UNIT",
            "value": "UNIT_label_fr",
        },
        inplace=True,
    )

    data["OBS_VALUE"] = pd.to_numeric(data["OBS_VALUE"])

    return data
