# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
import os
import warnings

from datetime import datetime

from pynsee.macrodata._get_dataset_metadata_core import _get_dataset_metadata_core
from pynsee.macrodata._get_idbank_internal_data import _get_idbank_internal_data
from pynsee.utils._hash import _hash
from pynsee.utils._create_insee_folder import _create_insee_folder


def _get_dataset_metadata(dataset, update=False):

    try:
        insee_folder = _create_insee_folder()
        file_dataset_metadata = insee_folder + \
            "/" + _hash("idbank_list" + dataset)

        trigger_update = False

        if not os.path.exists(file_dataset_metadata):
            trigger_update = True
            if not update:
                print(
                    "%s : metadata update triggered because it is not found locally" % dataset)
        else:

            try:
                # only used for testing purposes
                insee_date_time_now = os.environ['insee_date_test']
                insee_date_time_now = datetime.strptime(
                    insee_date_time_now, '%Y-%m-%d %H:%M:%S.%f')
            except:
                insee_date_time_now = datetime.now()

            # file date creation
            file_date_last_modif = datetime.fromtimestamp(
                os.path.getmtime(file_dataset_metadata))
            day_lapse = (insee_date_time_now - file_date_last_modif).days

            if day_lapse > 90:
                trigger_update = True
                if not update:
                    print(
                        "%s : metadata update triggered because the file is older than 3 months" % dataset)

        if update:
            trigger_update = True
            print("%s : metadata update triggered manually" % dataset)

        if trigger_update:

            idbank_list_dataset = _get_dataset_metadata_core(
                dataset=dataset, update=update)

            # save data
            idbank_list_dataset.to_pickle(file_dataset_metadata)
            # print("Data cached")
        else:
            # pickle format depends on python version
            # then read_pickle can fail, if so
            # the file is removed and the function is launched again
            # testing requires multiple python versions
            try:
                idbank_list_dataset = pd.read_pickle(file_dataset_metadata)
            except:
                os.remove(file_dataset_metadata)
                idbank_list_dataset = _get_dataset_metadata(
                    dataset, update=update)

            # print("Cached data has been used")
    except:
        # if the download of the idbank file and the build of the metadata fail
        # package's internal data is provided to the user, should be exceptional, used as a backup
        warnings.warn("\n!!! Warning: Package's internal data has been used !!!\n")
        print("!!! Idbank file download failed, have a look at the following page and find the new link !!!")
        print("https://www.insee.fr/en/information/2868055")
        print("!!! You may change the downloaded file changing the following environment variable !!!")
        print("import os; os.environ['pynsee_idbank_file'] = 'my_new_idbank_file'")
        print("!!! Please contact the package maintainer if this error persists !!!")

        idbank_list_dataset = _get_idbank_internal_data()
        idbank_list_dataset = idbank_list_dataset[idbank_list_dataset["DATASET"] == dataset]

        # drop the columns where all elements are NaN
        idbank_list_dataset = idbank_list_dataset.dropna(axis=1, how='all')
        idbank_list_dataset = idbank_list_dataset.reset_index(drop=True)

    return(idbank_list_dataset)
