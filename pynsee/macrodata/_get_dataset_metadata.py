# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
import os
import functools

from pynsee.macrodata._get_dataset_metadata_core import (
    _get_dataset_metadata_core,
)
from pynsee.macrodata._get_idbank_internal_data import (
    _get_idbank_internal_data,
)
from pynsee.utils.save_df import save_df

import logging

logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=None)
def _warning_error():
    logger.error(
            "Package's internal data has been used !\n"
            "Idbank file download failed, have a look at the following page "
            "and find the new link !\n"
            "https://www.insee.fr/en/information/2868055\n\n"
            "You may change the downloaded file changing the following "
            "environment variable !\n"
            "import os; os.environ['pynsee_idbank_file'] = 'my_new_idbank_file'\n"
            "Please contact the package maintainer if this error persists !"
        )

@save_df(day_lapse_max = 90)
def _get_dataset_metadata(dataset, update=False, silent=True, insee_date_test=None):

    try:
        idbank_list_dataset = _get_dataset_metadata_core(
                dataset=dataset, update=update, silent=True
            )
    except:
        # if the download of the idbank file and the build of the metadata fail
        # package's internal data is provided to the user, should be exceptional, used as a backup
        _warning_error()

        idbank_list_dataset = _get_idbank_internal_data(update=update)
        idbank_list_dataset = idbank_list_dataset[
            idbank_list_dataset["DATASET"] == dataset
        ]

        # drop the columns where all elements are NaN
        idbank_list_dataset = idbank_list_dataset.dropna(axis=1, how="all")
        idbank_list_dataset = idbank_list_dataset.reset_index(drop=True)

    return idbank_list_dataset