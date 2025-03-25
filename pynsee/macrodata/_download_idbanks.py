# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from datetime import date
import io
import logging
import os
import re
import warnings
import zipfile

import pandas as pd

from ..utils.requests_session import PynseeAPISession
from ..utils.save_df import save_df


logger = logging.getLogger(__name__)


@save_df(day_lapse_max=90)
def _download_idbank_list(
    update: bool = False,
    silent: bool = False,
):
    """
    Retrieve the correspondance between idbank and its dimensions; the result
    is cached.

    Parameters
    ----------
    update : bool, optional
        If True, a new download will be performed whatever the current cache's
        status. The default is False.
    silent : bool, optional
        If silent, will not log the caching. The default is False.

    Returns
    -------
    data : pd.DataFrame
        correspondance between idbank and it's dimensions as DataFrame

    """
    data = _dwn_idbank_files()

    data.columns = ["nomflow", "idbank", "cleFlow", "list_var"]

    data = data.sort_values("nomflow").reset_index(drop=True)

    return data


def _dwn_idbank_files() -> pd.DataFrame:
    """
    Retrieve the correspondance between idbank and its dimensions of today's
    date.

    Note: if `pynsee_idbank_file` is set (through an os environment variable),
    this value will be used to perform the download instead of the potential
    URLs tested by the inner loop. This should only be used manually if the
    current algorithm fails to retrieve the actual URL.

    Returns
    -------
    data : pd.DataFrame
        correspondance between idbank and it's dimensions as DataFrame
    """

    todays_date = date.today()

    main_link_en = "https://www.insee.fr/en/statistiques/fichier/2868055/"
    main_link_fr = "https://www.insee.fr/fr/statistiques/fichier/2862759/"

    curr_year = todays_date.year
    last_year = curr_year - 1
    years = [str(curr_year), str(last_year)]

    months = [str(x) for x in range(12, 9, -1)] + [
        "0" + str(x) for x in range(9, 0, -1)
    ]

    today = todays_date.strftime("%Y%m")
    patt = "_correspondance_idbank_dimension"
    patterns = [
        y + x + patt for y in years for x in months if not y + x > today
    ]
    files_en = [main_link_en + f + ".zip" for f in patterns]
    files_fr = [main_link_fr + f + ".zip" for f in patterns]
    files = files_fr + files_en

    idbank_file_not_found = True
    if "pynsee_idbank_file" in os.environ:
        file_to_dwn = os.environ["pynsee_idbank_file"]
        with PynseeAPISession() as session:
            try:
                data = _dwn_idbank_file(
                    file_to_dwn=file_to_dwn, session=session
                )
                idbank_file_not_found = False
            except Exception:
                pass

    i = 0
    with PynseeAPISession() as session:

        while idbank_file_not_found and i < len(files):
            try:
                data = _dwn_idbank_file(file_to_dwn=files[i], session=session)
            except Exception:
                idbank_file_not_found = True
            else:
                idbank_file_not_found = False
                strg_print = f"Macrodata series update, file used:\n{files[i]}"
                logger.info(strg_print)
            i += 1

    return data


def _dwn_idbank_file(
    file_to_dwn: str, session: PynseeAPISession
) -> pd.DataFrame:
    """
    Download and load the correspondance between idbank and its dimensions,
    knowing it's actual URL.

    Parameters
    ----------
    file_to_dwn : str
        URL to download the file from.
    session : PynseeAPISession
        Current Session used to perform the http request (inherits from
        requests.Session)

    Returns
    -------
    data : pd.DataFrame
        correspondance between idbank and it's dimensions as DataFrame

    """
    separator = ";"

    proxies = {}
    for key in ["http", "https"]:
        try:
            proxies[key] = os.environ[f"{key}_proxy"]
        except KeyError:
            proxies[key] = ""

    with warnings.catch_warnings():
        results = session.get(file_to_dwn, proxies=proxies, verify=False)

    idbank_zip_file = io.BytesIO(results.content)

    with zipfile.ZipFile(idbank_zip_file) as zip_ref:
        file_to_read = [
            f for f in zip_ref.namelist() if not re.match(".*.zip$", f)
        ]
        if len(file_to_read) == 0:
            # nested zipfile
            new_zip_file = [
                f for f in zip_ref.namelist() if re.match(".*.zip$", f)
            ][0]

            with zip_ref.open(new_zip_file) as nested_file:
                read = nested_file.read()

            with zipfile.ZipFile(io.BytesIO(read)) as new_zip_ref:
                file_to_read = [
                    f
                    for f in new_zip_ref.namelist()
                    if not re.match(".*.zip$", f)
                ][0]
                with new_zip_ref.open(file_to_read) as f:
                    content = f.read()
        else:
            with zip_ref.open(file_to_read[0]) as f:
                content = f.read()

    file2load = io.BytesIO(content)
    data = pd.read_csv(file2load, dtype="str", sep=separator)

    return data
