# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd


def _get_date(freq, time_period):

    # from datetime import datetime

    if freq == "M":
        dates = [tp + "-01" for tp in time_period]

    if freq == "A":
        dates = [tp + "-01-01" for tp in time_period]

    if freq == "T":
        dates = [tp.replace("-Q1", "-01-01") for tp in time_period]
        dates = [tp.replace("-Q2", "-04-01") for tp in dates]
        dates = [tp.replace("-Q3", "-07-01") for tp in dates]
        dates = [tp.replace("-Q4", "-10-01") for tp in dates]

    if freq == "S":
        dates = [tp.replace("-S1", "-01-01") for tp in time_period]
        dates = [tp.replace("-S2", "-07-01") for tp in dates]

    if freq == "B":
        dates = [tp.replace("-B1", "-01-01") for tp in time_period]
        dates = [tp.replace("-B2", "-03-01") for tp in dates]
        dates = [tp.replace("-B3", "-05-01") for tp in dates]
        dates = [tp.replace("-B4", "-07-01") for tp in dates]
        dates = [tp.replace("-B5", "-09-01") for tp in dates]
        dates = [tp.replace("-B6", "-11-01") for tp in dates]

    if freq not in ["M", "A", "S", "T", "B"]:
        dates = time_period
    else:
        # dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
        dates = pd.to_datetime(dates, format="%Y-%m-%d")

    return dates
