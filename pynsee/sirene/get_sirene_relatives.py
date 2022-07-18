import os
import sys
import pandas as pd
import re

from pynsee.utils._request_insee import _request_insee
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict


def get_sirene_relatives(*siret):
    """Find parent or child entities for one siret entity (etablissement)

    Args:
        siret (str or list): siret or list of siret codes

    Raises:
        ValueError: siret should be str or list

    Returns:
        pandas.DataFrame: dataframe containing the query content

    Examples:
        >>> # find parent or child entities for one siret entity (etablissement)
        >>> data = get_sirene_relatives('00555008200027')
        >>> data = get_sirene_relatives(['39860733300059', '00555008200027'])
    """

    list_siret = []

    for id in range(len(siret)):
        if isinstance(siret[id], list):
            list_siret += siret[id]
        elif isinstance(siret[id], pd.core.series.Series):
            list_siret += siret[id].to_list()
        elif isinstance(siret[id], str):
            list_siret += [siret[id]]
        else:
            list_siret += [str(siret[id])]

    types = ["siretEtablissementPredecesseur", "siretEtablissementSuccesseur"]
    list_df = []

    for s in range(len(list_siret)):
        for i in range(len(types)):

            criteria = types[i] + ":" + re.sub(r"\s+", "", list_siret[s])
            query = f"https://api.insee.fr/entreprises/sirene/V3/siret/liensSuccession?q={criteria}"
            try:
                sys.stdout = open(os.devnull, "w")
                result = _request_insee(
                    api_url=query, file_format="application/json;charset=utf-8"
                )
                json = result.json()
                sys.stdout = sys.__stdout__
            except:
                pass
            else:
                list_df += [_make_dataframe_from_dict(json)]

    if len(list_df) > 0:
        df = pd.concat(list_df).reset_index(drop=True)

        for c in ["statut", "message", "nombre", "total", "debut"]:
            if c in df.columns:
                del df[c]

        return df
    else:
        raise ValueError("Neither parent nor child entities were found for any entity")
