# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pynsee.utils._paste import _paste
from pynsee.macrodata._get_insee import _get_insee
from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata._add_numeric_metadata import _add_numeric_metadata
from pynsee.macrodata.get_series_list import get_series_list


def get_dataset(dataset,
                metadata=True,
                filter=None,
                startPeriod=None,
                endPeriod=None,
                firstNObservations=None,
                lastNObservations=None,
                includeHistory=None,
                updatedAfter=None):
    """Get dataset's data from INSEE BDM database

    Args:
        dataset (str): an INSEE dataset included in the list provided by get_dataset_list()

        metadata (bool, optional): If True, some metadata is added to the data

        filter (str, optional): Use the filter to choose only some values in a dimension.
        It is recommended to use it for big datasets. A dimension left empty means
        all values are selected. To select multiple values in one dimension put a "+" between those values.

        startPeriod (str, optional): start date of the data.

        endPeriod (str, optional): end date of the data.

        firstNObservations (int, optional): get the first N observations for each key series (idbank).

        lastNObservations (int, optional): get the last N observations for each key series (idbank).

        includeHistory (boolean, optional): boolean to access the previous releases (not available on all series).

        updatedAfter (str, optional): starting point for querying the previous releases (format yyyy-mm-ddThh:mm:ss)

    Raises:
        ValueError: dataset should be in INSEE's datasets list

    Returns:
        DataFrame: contains the data

    Examples:
        >>> from pynsee.macrodata import get_dataset
        >>> ipc_data = get_dataset("IPC-2015",
        >>>        filter = "M......ENSEMBLE...CVS.2015",
        >>>        includeHistory = True, updatedAfter = "2017-07-11T08:45:00")
        >>> #
        >>> business_climate = get_dataset("CLIMAT-AFFAIRES", lastNObservations = 1)
    """
    insee_dataset = get_dataset_list()
    insee_dataset_list = insee_dataset['id'].to_list()

    # check if the dataset exists in INSEE's list
    if dataset not in insee_dataset_list:
        raise ValueError("%s is not a dataset from INSEE" % dataset)

    INSEE_sdmx_link_idbank = "https://bdm.insee.fr/series/sdmx/data/"
    INSEE_api_link_idbank = "https://api.insee.fr/series/BDM/V1/data/"

    sdmx_query = INSEE_sdmx_link_idbank + dataset
    api_query = INSEE_api_link_idbank + dataset

    if filter is not None:
        sdmx_query = sdmx_query + "/" + str(filter)
        api_query = api_query + "/" + str(filter)

    parameters = ["startPeriod", "endPeriod",
                  "firstNObservations", "lastNObservations", "updatedAfter"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))

    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse='&')
        sdmx_query = sdmx_query + added_param_string
        if filter is None:
            api_query = api_query + "/" + added_param_string
        else:
            api_query = api_query + added_param_string

    # get data
    data = _get_insee(api_query=api_query, sdmx_query=sdmx_query)

    # add metadata
    if metadata:
        try:
            idbank_list = get_series_list(dataset)

            newcol = [
                col for col in idbank_list.columns if col not in data.columns] + ['IDBANK']
            idbank_list = idbank_list[newcol]

            data = data.merge(idbank_list, on='IDBANK', how='left')
            # remove all na columns
            data = data.dropna(axis=1, how='all')
        except:
            pass

        try:
            data = _add_numeric_metadata(data)
        except:
            pass

    
    return data
