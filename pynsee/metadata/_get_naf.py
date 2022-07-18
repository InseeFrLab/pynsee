# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd
import re


@lru_cache(maxsize=None)
def _get_naf(file):
    def clean_CODE_col(string):
        re_searched = re.search("^SECTION .*$", string)
        if re_searched:
            string_found = re_searched.group(0)
            string_found_cleaned = string_found.replace("SECTION ", "")
        else:
            string_found_cleaned = string
        return string_found_cleaned

    naf = pd.read_csv(
        file,
        sep=";",
        encoding="ISO-8859-1"
        # encoding='latin1'
    )

    # data cleaning
    naf = naf.iloc[:, 1:5]
    naf.columns = ["CODE", "TITLE_FR", "TITLE_65CH_FR", "TITLE_40CH_FR"]
    naf = naf.dropna()

    naf["CODE"] = naf["CODE"].apply(clean_CODE_col)

    naf["len_code"] = naf["CODE"].str.len()
    return naf
