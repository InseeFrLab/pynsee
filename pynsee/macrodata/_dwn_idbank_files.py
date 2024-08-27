from datetime import date
import io
import os
import zipfile
import re
import pandas as pd
import urllib3
import warnings

import logging

logger = logging.getLogger(__name__)

from pynsee.utils.requests_params import _get_requests_session


def _dwn_idbank_files():
    # creating the date object of today's date
    todays_date = date.today()

    main_link_en = "https://www.insee.fr/en/statistiques/fichier/2868055/"
    main_link_fr = "https://www.insee.fr/fr/statistiques/fichier/2862759/"

    curr_year = todays_date.year
    last_year = curr_year - 1
    years = [str(curr_year), str(last_year)]

    months = [str(x) for x in range(12, 9, -1)] + [
        "0" + str(x) for x in range(9, 0, -1)
    ]

    patt = "_correspondance_idbank_dimension"
    patterns = [y + x + patt for y in years for x in months]
    files_en = [main_link_en + f + ".zip" for f in patterns]
    files_fr = [main_link_fr + f + ".zip" for f in patterns]
    files = files_fr + files_en

    try:
        file_to_dwn = os.environ["pynsee_idbank_file"]
    except Exception:
        file_to_dwn = "https://www.insee.fr/fr/statistiques/fichier/2862759/202407_correspondance_idbank_dimension.zip"

    try:
        data = _dwn_idbank_file(file_to_dwn=file_to_dwn)
    except Exception:
        idbank_file_not_found = True
    else:
        idbank_file_not_found = False

    i = 0

    pynsee_idbank_loop_url = True

    try:
        pynsee_idbank_loop_url = os.environ["pynsee_idbank_loop_url"]
        if (pynsee_idbank_loop_url == "False") or (
            pynsee_idbank_loop_url == "FALSE"
        ):
            pynsee_idbank_loop_url = False
    except Exception:
        try:
            pynsee_idbank_loop_url = os.environ["PYNSEE_IDBANK_LOOP_URL"]
            if (pynsee_idbank_loop_url == "False") or (
                pynsee_idbank_loop_url == "FALSE"
            ):
                pynsee_idbank_loop_url = False
        except Exception:
            pass

    session = _get_requests_session()

    if pynsee_idbank_loop_url:
        while idbank_file_not_found & (i <= len(files) - 1):
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


def _dwn_idbank_file(file_to_dwn, session):
    separator = ";"

    proxies = {}
    for key in ["http", "https"]:
        try:
            proxies[key] = os.environ[f"{key}_proxy"]
        except KeyError:
            proxies[key] = ""

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore", urllib3.exceptions.InsecureRequestWarning
        )
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
