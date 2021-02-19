# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 16:34:43 2021

@author: XLAPDO
"""

from insee_macrodata import * 
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *

# get series key (idbank), for Gross domestic product balance
id = get_idbank_list("CNT-2014-PIB-EQB-RF")

id = id.loc[(id.FREQ == "T") &
            (id.OPERATION == "PIB") &
            (id.NATURE == "TAUX") &
            (id.CORRECTION == "CVS-CJO")]

data = get_insee_idbank(id.idbank)

# plot with plotly
fig = px.bar(data, x = data.index, y = "OBS_VALUE",
             facet_col = "TITLE_EN", facet_col_wrap=5)
fig.update_yaxes(matches=None)
plot(fig)


