# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 16:34:43 2021

@author: XLAPDO
"""

from insee_macrodata import * 
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *

df_idbank = get_idbank_list("IPC-2015")

df_idbank = df_idbank.loc[(df_idbank.FREQ == "M") & # monthly
                          (df_idbank.NATURE == "INDICE") & # index
                          (df_idbank.MENAGES_IPC == "ENSEMBLE") & # all kinds of household
                          (df_idbank.REF_AREA == "FE") & # all France including overseas departements
                          (df_idbank.COICOP2016.str.match("^[0-9]{2}$"))] # coicop aggregation level

# get data
data = get_insee_idbank(df_idbank.idbank)

# split title
df = split_title(data)

# replace title when missing and shorten it
rows = df["TITLE_EN6"].isnull()
df.loc[rows, "TITLE_EN6"] = df.loc[rows, "TITLE_EN5"]
df["TITLE_EN6"] = df["TITLE_EN6"].str[:22]

# compute year over year growth rate by IDBANK
df['pct_yoy'] = (df.OBS_VALUE/ df.groupby(['IDBANK']).OBS_VALUE.shift(12) - 1) * 100

# select dates after 2018-01-01
df = df.iloc[df.index >= "2018-01-01"]

# plot
fig = px.bar(df, x = df.index, y = "pct_yoy", color = "TITLE_EN6",
             facet_col = "TITLE_EN6", facet_col_wrap = 5)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
# fig.update_yaxes(matches=None)
fig.update_layout(showlegend=False)
plot(fig)

