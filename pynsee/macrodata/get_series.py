# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas
import math

from pynsee.macrodata._get_insee import _get_insee
from pynsee.macrodata.get_series_list import get_series_list
from pynsee.macrodata.search_macrodata import search_macrodata
from pynsee.macrodata._add_numeric_metadata import _add_numeric_metadata
from pynsee.utils._paste import _paste


def get_series(*idbanks,
               metadata=True,
               startPeriod=None,
               endPeriod=None,
               firstNObservations=None,
               lastNObservations=None,
               includeHistory=None,
               updatedAfter=None):
    """Get data from INSEE series idbank

    Args:
        idbanks (str or list or pd.series) : some idbanks provided by get_idbank_list()

        metadata (bool, optional): If True, some metadata is added to the data

        startPeriod (str, optional): start date of the data.

        endPeriod (str, optional): end date of the data.

        firstNObservations (int, optional): get the first N observations for each key series (idbank).

        lastNObservations (int, optional): get the last N observations for each key series (idbank).

        includeHistory (boolean, optional): boolean to access the previous releases (not available on all series).

        updatedAfter (str, optional): starting point for querying the previous releases (format yyyy-mm-ddThh:mm:ss)

    Returns:
        DataFrame: contains the data, indexed by DATE and sorted by IDBANK

    Examples:
        >>> from pynsee.macrodata import get_series_list, get_series
        >>> # inflation figures in France
        >>> df_idbank = get_series_list("IPC-2015")
        >>> df_idbank = df_idbank.loc[
        >>>                    (df_idbank.FREQ == "M") & # monthly
        >>>                    (df_idbank.NATURE == "INDICE") & # index
        >>>                    (df_idbank.MENAGES_IPC == "ENSEMBLE") & # all kinds of household
        >>>                    (df_idbank.REF_AREA == "FE") & # all France including overseas departements
        >>>                    (df_idbank.COICOP2016.str.match("^[0-9]{2}$"))] # coicop aggregation level
        >>> # get data
        >>> data = get_series(df_idbank.IDBANK)
    """
    INSEE_sdmx_link_idbank = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/"
    INSEE_api_link_idbank = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/"

    #
    # create the parameters to be added to the query
    #

    parameters = ["startPeriod", "endPeriod",
                  "firstNObservations", "lastNObservations", "updatedAfter"]

    list_addded_param = []
    for param in parameters:
        if eval(param) is not None:
            list_addded_param.append(param + "=" + str(eval(param)))

    added_param_string = ""
    if len(list_addded_param) > 0:
        added_param_string = "?" + _paste(list_addded_param, collapse='&')

    #
    # make one single list of idbanks
    #

    list_idbank = []

    for id in range(len(idbanks)):
        if isinstance(idbanks[id], list):
            list_idbank = list_idbank + idbanks[id]
        elif isinstance(idbanks[id], pandas.core.series.Series):
            list_idbank = list_idbank + idbanks[id].to_list()
        elif isinstance(idbanks[id], str):
            list_idbank = list_idbank + [idbanks[id]]
        else:
            list_idbank = list_idbank + [idbanks[id]]

    #
    # create the ranges of the queries
    # mutliple queries will be created each with 400 idbanks
    #

    n_idbank = len(list_idbank)
    idbank_limit = 400
    max_seq_idbank = math.ceil(n_idbank / idbank_limit)

    list_data = []

    for q in range(max_seq_idbank):

        min_range = q * idbank_limit
        max_range = min((q + 1) * idbank_limit, n_idbank + 1)

        list_idbank_q = list_idbank[min_range:max_range]

        sdmx_query = INSEE_sdmx_link_idbank + \
            _paste(list_idbank_q, collapse='+')
        api_query = INSEE_api_link_idbank + \
            _paste(list_idbank_q, collapse='%2B')

        if len(list_addded_param) > 0:
            sdmx_query = sdmx_query + added_param_string
            # api_query = api_query + "/" + added_param_string
            api_query = api_query + added_param_string

        df = _get_insee(api_query=api_query,  # api_query
                        sdmx_query=sdmx_query,
                        step=str("{0}/{1}").format(q + 1, max_seq_idbank))

        list_data.append(df)

    data = pandas.concat(list_data)

    if metadata:
        try:
            all_idbank = search_macrodata()
            list_all_idbank = all_idbank.IDBANK.to_list()

            list_data_idbank = data.IDBANK.unique()
            idbank_available_bool = [(idb in list_all_idbank)
                                     for idb in list_data_idbank]

            if any(idbank_available_bool):

                idbank_available = list_data_idbank[idbank_available_bool]
                list_dataset = all_idbank[all_idbank.IDBANK.isin(
                    idbank_available)]
                list_dataset = list(list_dataset.DATASET.unique())

                idbank_list = get_series_list(list_dataset)
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
