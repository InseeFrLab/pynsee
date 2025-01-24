import os
import re
from tqdm import trange
import datetime
import pickle
import pandas as pd

from pynsee.localdata._get_insee_local_onegeo import _get_insee_local_onegeo
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from pynsee.utils.HiddenPrints import HiddenPrints

import logging

logger = logging.getLogger(__name__)


def _find_latest_local_dataset(
    dataset_version, variables, nivgeo, codegeo, update, backwardperiod=6
):

    filename = _hash(
        "".join([dataset_version] + ["_find_latest_local_dataset"])
    )
    insee_folder = _create_insee_folder()
    file_localdata = insee_folder + "/" + filename

    if (not os.path.exists(file_localdata)) or update:

        datasetname = dataset_version.replace("latest", "").replace("GEO", "")

        current_year = int(datetime.datetime.today().strftime("%Y"))

        list_geo_dates = range(current_year, current_year - backwardperiod, -1)
        list_data_dates = range(
            current_year, current_year - backwardperiod, -1
        )

        if re.compile("^GEOlatest.*latest$").match(dataset_version):

            list_dataset_version = [
                "GEO" + str(gdate) + datasetname + str(ddate)
                for gdate in list_geo_dates
                for ddate in list_data_dates
            ]
        else:
            list_dataset_version = [
                datasetname + str(ddate) for ddate in list_data_dates
            ]

        for dvindex in trange(
            len(list_dataset_version), desc="Finding Latest Dataset Version"
        ):

            dv = list_dataset_version[dvindex]

            try:
                with HiddenPrints():
                    df = _get_insee_local_onegeo(
                        variables, dv, nivgeo=nivgeo, codegeo=codegeo
                    )

                if isinstance(df, pd.DataFrame):
                    if len(df.index) == 1:
                        if df["OBS_VALUE"][0] is None:
                            raise ValueError("No data found")

            except Exception:
                if dv == list_dataset_version[-1]:
                    msg = (
                        "!!! Latest dataset version not found !!!\n"
                        "Please, consider having a look at api.insee.fr or "
                        "get_local_metadata function"
                    )
                    raise ValueError(msg)
            else:
                dataset_version = dv
                break

        f = open(file_localdata, "wb")
        pickle.dump(str(dataset_version), f)
        f.close()
    else:
        try:
            f = open(file_localdata, "rb")
            dataset_version = pickle.load(f)
            f.close()
        except Exception:
            os.remove(file_localdata)
            dataset_version = _find_latest_local_dataset(
                variables=variables,
                dataset_version=dataset_version,
                update=True,
            )
        else:
            logger.info(
                "Latest dataset version previously found has been used\n"
                "Set update=True to get the most up-to-date data"
            )

    return dataset_version
