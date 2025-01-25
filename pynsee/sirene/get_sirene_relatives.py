import pandas as pd
import re

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils._make_dataframe_from_dict import _make_dataframe_from_dict
from pynsee.utils.HiddenPrints import HiddenPrints
from pynsee.sirene.SireneDataFrame import SireneDataFrame


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
            query = f"https://api.insee.fr/api-sirene/3.11/siret/liensSuccession?q={criteria}"
            try:
                with HiddenPrints():
                    with PynseeAPISession() as session:
                        result = session.request_insee(
                            api_url=query,
                            file_format="application/json;charset=utf-8",
                            raise_if_not_ok=True,
                            print_msg=False,
                        )

                    json = result.json()
            except:
                pass
            else:
                list_df += [_make_dataframe_from_dict(json)]

    if len(list_df) > 0:
        df = SireneDataFrame(pd.concat(list_df).reset_index(drop=True))

        for c in ["statut", "message", "nombre", "total", "debut"]:
            if c in df.columns:
                del df[c]

        return df
    else:
        raise ValueError(
            "Neither parent nor child entities were found for any entity"
        )
