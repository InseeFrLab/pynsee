# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pkg_resources
import pandas as pd


def _get_installed_packages():

    installed_packages = pkg_resources.working_set

    df = pd.DataFrame({"package": None, "version": None}, index=[0])
    j = 0
    for i in installed_packages:
        df.loc[j, "package"], df.loc[j, "version"] = i.key, i.version
        j += 1

    df = df.sort_values("package").reset_index(drop=True)

    return df
