# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021


from functools import lru_cache
import logging
import xml.etree.ElementTree as ET

import pandas as pd

from pynsee.utils.requests_session import PynseeAPISession


logger = logging.getLogger(__name__)


def _set_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dates on a dataframe issued by macrodata module.

    Adds a "DATE" first column (computed from the "TIME_PERIOD" original
    column) and sort the dataframe according to it.

    Internal note: leave this as a separate function to to improve tests

    coverage.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least two columns: "FREQ" and "TIME_PERIOD".
        The FREQ column should contain only one homogeneous value.

    Returns
    -------
    df : pd.DataFrame
    """

    freqs = df.FREQ.unique()
    if "DATE" not in df.columns:
        df["DATE"] = None

    for freq in freqs:
        ix = df[df.FREQ == freq].index
        time = df.loc[ix, "TIME_PERIOD"]
        if freq == "M":
            df.loc[ix, "DATE"] = time + "-01"

        elif freq == "A":
            df.loc[ix, "DATE"] = time + "-01-01"

        elif freq in {"T", "S", "B"}:

            if freq == "T":
                pat = "(-Q[1234])"
                repl = {
                    "-Q1": "-01-01",
                    "-Q2": "-04-01",
                    "-Q3": "-07-01",
                    "-Q4": "-10-01",
                }
            elif freq == "S":
                pat = "(-S[12])"
                repl = {"-S1": "-01-01", "-S2": "-07-01"}
            elif freq == "B":
                pat = "(-B[123456])"
                repl = {
                    "-B1": "-01-01",
                    "-B2": "-03-01",
                    "-B3": "-05-01",
                    "-B4": "-07-01",
                    "-B5": "-09-01",
                    "-B6": "-11-01",
                }

            df.loc[ix, "DATE"] = time.str[:-3] + time.str.extract(
                pat, expand=False
            ).map(repl)
        else:
            df.loc[ix, "DATE"] = time

        if freq in {"M", "A", "S", "T", "B"}:
            df.loc[ix, "DATE"] = pd.to_datetime(
                df.loc[ix, "DATE"], format="%Y-%m-%d"
            )

    if "DATE" in df.columns:
        # place DATE column in the first position and sort
        df[["DATE"] + [c for c in df.columns if c not in ["DATE"]]]
        df = df.sort_values(["IDBANK", "DATE"]).reset_index(drop=True)

    return df


@lru_cache(maxsize=None)
def _get_insee(api_query, sdmx_query, step="1/1"):

    with PynseeAPISession() as session:
        results = session.request_insee(sdmx_url=sdmx_query, api_url=api_query)

    # parse the xml file
    root = ET.fromstring(results.content)

    obs_series = []
    series = root.findall(".//Series")
    for serie in series:
        dict_attr = serie.attrib
        obs = [obs.attrib for obs in serie.iterfind("./")]
        [x.update(dict_attr) for x in obs]
        obs_series += obs
    data = pd.DataFrame(obs_series)

    data = _set_date(data)

    # harmonise column names
    colnames = data.columns

    def replace_hyphen(x):
        return str(x).replace("-", "_")

    newcolnames = list(map(replace_hyphen, colnames))
    data.columns = newcolnames

    if "OBS_VALUE" in data.columns:
        data["OBS_VALUE"] = data["OBS_VALUE"].apply(
            pd.to_numeric, errors="coerce"
        )

    logger.debug("Data has been cached")

    return data
