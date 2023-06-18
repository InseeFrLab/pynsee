import os
import pandas as pd
from functools import lru_cache
import difflib
import logging

from pynsee.download._unzip_pb import _unzip_pb

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def warning_file(missingFile, foundFile):
    msgs = [("error", f"Data file missing in the zip file: {missingFile}")]
    if not foundFile == "":
        msgs.append(
            ("error", f"Following file has been used instead: {foundFile}")
        )
    else:
        msgs.append(("warning", "No replacement file has been found"))
    msgs.append(("error", "Please report this issue !"))
    for level, msg in msgs:
        getattr(logger, level)(msg)


def _load_data_from_schema(
    telechargementFichier: dict, variables=None, limit_chunk_size=1000000000
):
    """Using options derived from `download_store_file`, import dataset in python

    Arguments:
        telechargementFichier {dict} -- Options needed for import

    Keyword Arguments:
        variables {list} -- A subset of variables that should be used (default: {None})

    Raises:
        ValueError: If the file is not found, an error is raised

    Returns:
        pd.DataFrame -- The required dataset is returned as pd.DataFrame object
    """
    file_to_import = telechargementFichier["file_to_import"]

    if telechargementFichier["result"]["zip"] is True:
        zipDirectory = f"{telechargementFichier['import_args']['file']}_temp"

        _unzip_pb(telechargementFichier["file_archive"], f"{zipDirectory}")

        dataFile = telechargementFichier["result"]["fichier_donnees"]
        dataPathFile = f"{zipDirectory}/{dataFile}"

        if not os.path.exists(dataPathFile):
            list_file_dir = os.listdir(zipDirectory)

            suggestions = difflib.get_close_matches(
                dataFile, list_file_dir, n=1
            )

            if not len(suggestions) == 0:
                foundFile = suggestions[0]
                file_to_import = f"{zipDirectory}/{foundFile}"
            else:
                foundFile = ""

            warning_file(missingFile=dataFile, foundFile=foundFile)
        else:
            file_to_import = dataPathFile

    if os.path.isfile(file_to_import) is False:
        raise ValueError("File cannot be found")

    if telechargementFichier["result"]["type"] == "csv":
        # big file data load
        if os.path.getsize(file_to_import) >= limit_chunk_size:
            list_chunk = []
            chunksize = 10**6
            with pd.read_csv(
                file_to_import,
                chunksize=chunksize,
                dtype="str",
                usecols=variables,
                delimiter=telechargementFichier["import_args"]["delim"],
            ) as reader:
                for chunk in reader:
                    list_chunk += [chunk]

            df_insee = pd.concat(list_chunk)
        else:
            try:
                df_insee = pd.read_csv(
                    file_to_import,
                    delimiter=telechargementFichier["import_args"]["delim"],
                    dtype="str",
                    usecols=variables,
                )
            except:
                encoding = telechargementFichier["import_args"]["encoding"]
                useEncoding = True
                if isinstance(encoding, str):
                    if encoding == "Nan":
                        useEncoding = False
                else:
                    useEncoding = False

                if not useEncoding:
                    df_insee = pd.read_csv(
                        file_to_import,
                        delimiter=telechargementFichier["import_args"][
                            "delim"
                        ],
                        dtype="str",
                        usecols=variables,
                        engine="python",
                    )
                else:
                    df_insee = pd.read_csv(
                        file_to_import,
                        delimiter=telechargementFichier["import_args"][
                            "delim"
                        ],
                        dtype="str",
                        usecols=variables,
                        engine="python",
                        encoding=encoding,
                    )

    elif telechargementFichier["result"]["type"] in ["xls", "xlsx"]:
        df_insee = pd.read_excel(
            file_to_import,
            sheet_name=telechargementFichier["import_args"]["sheet"],
            skiprows=telechargementFichier["import_args"]["skip"],
            nrows=telechargementFichier["import_args"]["n_max"],
            na_values=telechargementFichier["import_args"]["na"],
            dtype="str",
            usecols=variables,
        )

    return df_insee
