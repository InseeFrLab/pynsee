# -*- coding: utf-8 -*-
"""
Download MELODI's catalog.

Only one endpoint is covered by pynsee, as "catalog/{id}" and "catalog/ids"
are covered using in "catalog/all" (which is slowest but cache handled by
pynsee bypasses that).

Thus, the only endpoint NOT yet covered is "/catalog/dcat".
"""

import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=30)
def get_melodi_catalog(language: str = "all") -> pd.DataFrame:
    """
    Retrieve MELODI's full catalog.

    Parameters
    ----------
    language : str, optional
        Filter metadata to select a desired language, if available. The default
        is "all", which won't filter anything. Covered values are "fr", "en".

    Returns
    -------
    dataset : pd.DataFrame

    Ex:
                                                   accessURL  byteSize format  \
        0  https://api.insee.fr/melodi/file/DD_CNA_AGREGA...   1895856    CSV
        1  https://api.insee.fr/melodi/file/DD_CNA_BRANCH...   3551601    CSV

                               id               issued language mediaType  \
        0  DD_CNA_AGREGATS_CSV_FR  2024-07-18T15:46:53       FR  text/csv
        1  DD_CNA_BRANCHES_CSV_FR  2024-11-22T13:11:59       FR  text/csv

                      modified    packageFormat  \
        0  2025-08-29T13:38:30  application/zip
        1  2025-05-27T17:45:13  application/zip

                                                       title dataset_identifier  \
        0  Produit Intérieur Brut (PIB) et grands agrégat...    DD_CNA_AGREGATS
        1                Activité des branches de l'économie    DD_CNA_BRANCHES

                                                 abstract_fr  \
        0  Données annuelles de Produit Intérieur Brut (P...
        1  Données annuelles sur l'activité des branches ...

                                                 abstract_en accessRights_fr  \
        0  Annual data on Gross Domestic Product (GDP) an...           Libre
        1  Annual data on the activity of branches within...           Libre

          accrualPeriodicity_fr accrualPeriodicity_en confidentialityStatus_fr  \
        0                Annuel                Annual                    Libre
        1                Annuel                Annual                    Libre

          creator                                     description_fr  \
        0   Insee  Le produit intérieur brut (PIB) est le princip...
        1   Insee  Données annuelles sur l'activité des branches ...

                                              description_en  \
        0  Gross domestic product (GDP) is the main aggre...
        1  Annual data on the activity of industries as r...

                                             ordreComposants processStep_fr  \
        0  ACCOUNTING_ENTRY, ACTIVITY, COUNTERPART_AREA, ...       inseeApi
        1  REF_SECTOR, COUNTERPART_AREA, ACCOUNTING_ENTRY...       inseeApi

          processStep_en                                       publisher_fr  \
        0       inseeApi  Institut national de la statistique et des etu...
        1       inseeApi  Institut national de la statistique et des etu...

                                                publisher_en  \
        0  National Institute of Statistics and Economic ...
        1  National Institute of Statistics and Economic ...

                                                scopeNote_fr  \
        0
        1  La version du dataset mise en ligne le 8 octob...

                                                scopeNote_en      spatial_fr  \
        0                                                     France entière
        1  The version of the dataset published online on...  France entière

          spatial_en          dsd                            subtitle_fr  \
        0     France  DSD_NA_MAIN  Comptes nationaux annuels - Base 2020
        1     France  DSD_NA_MAIN  Comptes nationaux annuels - Base 2020

                             subtitle_en            endPeriod          startPeriod  \
        0     Base 2020 - Annual Results  2024-01-01T00:00:00  1949-01-01T00:00:00
        1  National accounts - Base 2020  2024-01-01T00:00:00  1949-01-01T00:00:00

                                                    title_fr  \
        0  Produit Intérieur Brut (PIB) et grands agrégat...
        1                Activité des branches de l'économie

                                                    title_en           type_fr  \
        0  Gross domestic product (GDP) and main economic...  Données agrégées
        1    Production and generation of income by industry  Données agrégées

                                                         uri  \
        0  http://id.insee.fr/catalogues/jeuDeDonnees/8b0...
        1  http://id.insee.fr/catalogues/jeuDeDonnees/a85...

                                           uuid accessRights_en type_en  \
        0  2ccb4960-fb78-4ef9-93f6-2edf14cb53c8            None    None
        1  2017dbc2-177f-29d7-4f74-749965615961            None    None

          confidentialityStatus_en spatialTemporal
        0                     None            None
        1                     None            None

    Examples
    ----------
    >>> get_melodi_catalog()
    >>> get_melodi_catalog(language="fr")
    """

    url = "https://api.insee.fr/melodi/catalog/all"

    with PynseeAPISession() as session:

        r = session.request_insee(api_url=url, file_format="application/json")

    list_data_dict = []
    list_product_dict = []

    for dset in r.json():
        dico = {}
        for metadata, meta_description in dset.items():
            if isinstance(meta_description, list):
                if all(isinstance(j, str) for j in meta_description):
                    dico[metadata] = ", ".join(meta_description)
                for d2 in meta_description:
                    if isinstance(d2, dict):
                        if all(j in d2.keys() for j in ["lang", "content"]):
                            if language in {"all", d2["lang"]}:
                                dico[metadata + "_" + d2["lang"]] = d2[
                                    "content"
                                ]
            elif isinstance(meta_description, dict):
                try:
                    for d2 in meta_description["label"]:
                        if language in {"all", d2["lang"]}:
                            dico[metadata + "_" + d2["lang"]] = d2["content"]
                except KeyError:
                    dico.update(meta_description)

            elif isinstance(meta_description, str):
                dico[metadata] = meta_description

        list_data_dict += [dico]

        if "product" in dset.keys():
            if isinstance(dset["product"], list):
                for product in dset["product"]:
                    if isinstance(product, dict):
                        product["identifier"] = dset["identifier"]
                        list_product_dict += [product]

    meta = pd.DataFrame(list_data_dict)
    products = pd.DataFrame(list_product_dict)
    list_col_dropped = [
        c
        for c in products.columns
        if (c in meta.columns) and (c != "identifier")
    ]
    meta2 = meta.drop(columns=list_col_dropped)

    dataset = products.merge(meta2, on="identifier", how="left").rename(
        columns={"identifier": "dataset_identifier"}
    )

    return dataset
