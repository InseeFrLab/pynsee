# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from tqdm import trange
import numpy as np
from requests.exceptions import RequestException

from pynsee.utils._paste import _paste
from pynsee.localdata._get_geo_relation import _get_geo_relation
from pynsee.localdata._get_geo_list_simple import _get_geo_list_simple

from pynsee.utils.save_df import save_df


@save_df(day_lapse_max=90)
def get_geo_list(geo=None, date=None, update=False, silent=False):
    """Get a list of French geographic areas (communes, departements, regions ...)

    Args:
        geo (str): choose among : communes, communesDeleguees, communesAssociees, regions, departements, arrondissements, arrondissementsMunicipaux

        date (str): date of validity (AAAA-MM-DD)

        update (bool): locally saved data is used by default. Trigger an update with update=True.

        silent (bool, optional): Set to True, to disable messages printed in log info
    Raises:
        ValueError: geo should be among the geographic area list

    Examples:
        >>> from pynsee.localdata.get_geo_list import get_geo_list
        >>> city_list = get_geo_list('communes')
        >>> region_list = get_geo_list('regions')
        >>> departement_list = get_geo_list('departements')
        >>> arrondiss_list = get_geo_list('arrondissements')
    """

    list_available_geo = [
        "communes",
        "communesDeleguees",
        "communesAssociees",
        "regions",
        "departements",
        "arrondissements",
        "arrondissementsMunicipaux",
    ]
    geo_string = _paste(list_available_geo, collapse=" ")

    error_msg = False

    if geo is None:
        error_msg = True
    elif geo not in list_available_geo:
        error_msg = True

    if error_msg:
        msg = "!!! Please choose geo among:\n{}".format(geo_string)
        raise ValueError(msg)

    reg = _get_geo_list_simple("regions", date=date, progress_bar=True)
    reg["DATESUPPRESSION"] = reg.get("DATESUPPRESSION", np.nan)

    if geo != "regions":
        list_reg = list(reg.CODE)
        list_data_reg = []

        if geo != "arrondissementsMunicipaux":
            type_geo = geo.rstrip("s")
        else:
            type_geo = "ArrondissementMunicipal"

        for r in trange(
            len(list_reg), desc="Getting {}".format(geo), leave=False
        ):
            try:
                df = _get_geo_relation(
                    geo="region",
                    code=list_reg[r],
                    relation="descendants",
                    date=date,
                    type=type_geo,
                )
            except (RequestException, SyntaxError):
                df = _get_geo_relation(
                    geo="region",
                    code=list_reg[r],
                    relation="descendants",
                    date=date,
                    type=None,
                )

            finally:
                list_data_reg.append(df)

        data_all = pd.concat(list_data_reg)

        reg_short = reg[["TITLE", "CODE"]]
        reg_short.columns = ["TITLE_REG", "CODE_REG"]
        data_all = data_all.merge(
            reg_short, how="left", left_on="geo_init", right_on="CODE_REG"
        )

        if geo == "communes":
            data_all = data_all.loc[
                data_all["TYPE"].str.match("^Commune$", na=False)
            ]
        if geo == "communesDeleguees":
            data_all = data_all.loc[
                data_all["TYPE"].str.match("^CommuneDeleguee$", na=False)
            ]
        if geo == "communesAssociees":
            data_all = data_all.loc[
                data_all["TYPE"].str.match("^CommuneAssociee$", na=False)
            ]
        if geo == "arrondissements":
            data_all = data_all.loc[
                data_all["TYPE"].str.match("^Arrondissement$", na=False)
            ]
        if geo == "arrondissementsMunicipaux":
            data_all = data_all.loc[
                data_all["TYPE"].str.match(
                    "^ArrondissementMunicipal$", na=False
                )
            ]
        if geo == "departements":
            data_all = data_all.loc[
                data_all["TYPE"].str.match("^Departement$", na=False)
            ]

        try:
            data_all = data_all.drop("geo_init", axis=1)
        except KeyError:
            pass

        if geo != "departements":
            dep = _get_geo_list_simple(
                "departements", date=date, progress_bar=True
            )
            dep_short = dep[["CODE", "TITLE"]]
            dep_short.columns = ["CODE_dep", "TITLE_DEP1"]

            dep_short2 = dep[["CODE", "TITLE"]]
            dep_short2.columns = ["CODE_dep", "TITLE_DEP2"]

            data_all = data_all.assign(
                code_dep1=data_all["CODE"].str[:2],
                code_dep2=data_all["CODE"].str[:3],
            )

            data_all = data_all.merge(
                dep_short,
                how="left",
                left_on="code_dep1",
                right_on="CODE_dep",
            )
            data_all = data_all.merge(
                dep_short2,
                how="left",
                left_on="code_dep2",
                right_on="CODE_dep",
            )

            for i in range(len(data_all.index)):
                if pd.isna(data_all.loc[i, "TITLE_DEP1"]):
                    data_all.loc[i, "CODE_DEP"] = data_all.loc[i, "code_dep2"]
                    data_all.loc[i, "TITLE_DEP"] = data_all.loc[
                        i, "TITLE_DEP2"
                    ]
                else:
                    data_all.loc[i, "CODE_DEP"] = data_all.loc[i, "code_dep1"]
                    data_all.loc[i, "TITLE_DEP"] = data_all.loc[
                        i, "TITLE_DEP1"
                    ]

            data_all = data_all.drop(
                [
                    "code_dep1",
                    "code_dep2",
                    "CODE_dep_x",
                    "CODE_dep_y",
                    "TITLE_DEP1",
                    "TITLE_DEP2",
                ],
                axis=1,
            )

        df_geo = data_all
    else:
        df_geo = reg

    return df_geo
