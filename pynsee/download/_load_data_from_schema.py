import os
import pandas as pd
from functools import lru_cache
import difflib
import logging

from openpyxl.styles.colors import WHITE, RGB, aRGB_REGEX

from pynsee.download._unzip_pb import _unzip_pb

logger = logging.getLogger(__name__)


def _patch_read_excel_aRGB_hex_values(func):
    """
    patch openpyxl to avoid raising ValueError because of colors styling
    """

    def __patch_set__(self, instance, value):
        if not self.allow_none:
            m = aRGB_REGEX.match(value)
            if m is None:
                value = WHITE
            if len(value) == 6:
                value = "00" + value
        super(RGB, self).__set__(instance, value)

    def wrapper(*args, **kwargs):
        __old_rgb_set__ = RGB.__set__
        try:
            RGB.__set__ = __patch_set__
            return func(*args, **kwargs)
        except Exception:
            raise
        finally:
            RGB.__set__ = __old_rgb_set__

    return wrapper


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


@_patch_read_excel_aRGB_hex_values
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
    df_insee = None
    file_to_import = telechargementFichier["file_to_import"]

    if telechargementFichier["result"]["zip"] is True:
        zipDirectory = f"{telechargementFichier['import_args']['file']}_temp"

        _unzip_pb(telechargementFichier["file_archive"], f"{zipDirectory}")

        dataFile = telechargementFichier["result"]["fichier_donnees"]
        dataPathFile = os.path.join(f"{zipDirectory}", f"{dataFile}")

        if not os.path.exists(dataPathFile):
            list_file_dir = os.listdir(zipDirectory)

            suggestions = difflib.get_close_matches(
                dataFile, list_file_dir, n=1
            )

            if not len(suggestions) == 0:
                foundFile = suggestions[0]
                file_to_import = os.path.join(
                    f"{zipDirectory}", f"{foundFile}"
                )
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
            except Exception:
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
    elif telechargementFichier["result"]["type"] == "parquet":
        df_insee = pd.read_parquet(file_to_import, columns=variables)

    list_files = [file_to_import]

    if telechargementFichier["result"]["zip"] is True:
        list_files += [
            dataPathFile,
            os.path.join(
                f"{zipDirectory}", telechargementFichier["file_archive"]
            ),
            telechargementFichier["file_archive"],
        ]

    for f in list_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    if df_insee is None:
        raise RuntimeError(
            f"Unexpected download data:\n{telechargementFichier}"
        )

    return df_insee
