import pandas as pd
import re

from requests import RequestException

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict
from .sirenedataframe import SireneDataFrame


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

    for s in list_siret:
        for t in types:
            criteria = t + ":" + re.sub(r"\s+", "", s)
            query = (
                "https://api.insee.fr/api-sirene/3.11/siret/liensSuccession"
                f"?q={criteria}"
            )

            try:
                with PynseeAPISession() as session:
                    result = session.request_insee(
                        api_url=query,
                        file_format="application/json;charset=utf-8",
                        raise_if_not_ok=True,
                        print_msg=False,
                    )

                json = result.json()
            except RequestException as e:
                if e.response.status_code == 401:
                    raise
            except Exception:
                pass
            else:
                list_df += [_make_dataframe_from_dict(json)]

    if list_df:
        df = SireneDataFrame(
            pd.concat(list_df)
            .drop(
                columns=["statut", "message", "nombre", "total", "debut"],
                errors="ignore",
            )
            .reset_index(drop=True)
        )

        if df.columns.any():
            return df

    raise ValueError(
        "Neither parent nor child entities were found for any entity"
    )
