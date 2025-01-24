#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pynsee import *
import copy
import pandas as pd
import numpy as np
import seaborn as sns

files = get_file_list()

files[files["collection"] == "RP"][["id", "label"]].to_csv("rp.csv")


# In[46]:


geodata_files = get_geodata_list()
geodata_files.to_csv("geodata_files.csv")


# In[59]:


epci = get_geodata("ADMINEXPRESS-COG-CARTO.LATEST:epci")


# In[50]:


epci.head(5)


# In[ ]:


epci2 = ()


# In[2]:


col = get_column_metadata("RP_MOBPRO_2016")
col.to_csv("rp_col.csv")

col2 = col[["column", "column_label_fr"]].drop_duplicates()
col2.to_csv("rp_col2.csv")


# In[3]:


col[col["column"] == "TRANS"]


# In[4]:


dfraw = download_file("RP_MOBPRO_2017")

list_col = ["COMMUNE", "ARM", "DCLT"]
idf = dfraw[dfraw["REGION"] == "11"]

com = get_geodata("ADMINEXPRESS-COG-CARTO.LATEST:commune")


# In[5]:


arr = get_geodata("ADMINEXPRESS-COG-CARTO.LATEST:arrondissement_municipal")
arr75 = arr[arr["insee_com"].str.contains("^75")]
arr75 = arr75.drop("insee_com", axis=1).rename(
    columns={"insee_arm": "insee_com"}
)
arr75 = arr75[["insee_com", "geometry", "nom"]]
arr75.head(3)


# In[6]:


comIDF = com[com["insee_reg"] == "11"].reset_index(drop=True)
comIDF = comIDF[comIDF["insee_com"] != "75056"][
    ["insee_com", "geometry", "nom"]
]
idfgeo = pd.concat([arr75, comIDF]).reset_index(drop=True)

idfgeo["center"] = idfgeo["geometry"].apply(lambda x: x.centroid)

IDFGEO = copy.copy(idfgeo)
del idfgeo["geometry"]
idfgeo.head()


# In[7]:


dfraw[(dfraw["REGION"] == "11") & (dfraw["COMMUNE"] != "75056")].head(100)


# In[8]:


idfData = idf.copy()


# In[9]:


idf.columns


# In[10]:


idfgeo1 = idfgeo.copy()
idfgeo1.columns = [
    "COMMUNE",
    "COMMUNE_NAME",
    "COMMUNE_CENTER",
]
idfgeo2 = idfgeo.copy()
idfgeo2.columns = [
    "DCLT",
    "DCLT_NAME",
    "DCLT_CENTER",
]


# In[11]:


from shapely.geometry import LineString


def make_line(p1, p2):
    return LineString([p1, p2])


# In[12]:


import pandas as pd

list_col_group = ["COMMUNE", "DCLT"]

dfraw2 = dfraw[(dfraw["REGION"] == "11")]  # & (dfraw['COMMUNE'] != '75056')
dfraw2.iloc[:, dfraw2.columns.get_loc("COMMUNE")] = np.where(
    dfraw2["COMMUNE"] == "75056", dfraw2["ARM"], dfraw2["COMMUNE"]
)
dfraw2.iloc[:, dfraw2.columns.get_loc("IPONDI")] = pd.to_numeric(
    dfraw2["IPONDI"]
)


# In[13]:


dfraw2.columns


# In[14]:


idfData = (
    dfraw2.groupby(list_col_group, as_index=False)["IPONDI"]
    .agg("sum")
    .merge(idfgeo1, on="COMMUNE", how="left")
    .merge(idfgeo2, on="DCLT", how="left")
    .reset_index()
    .dropna()
)
idfData[idfData["COMMUNE"].str.contains("^75")].head(3)


# In[15]:


idfData.head(3)


# In[16]:


idfData["line"] = idfData.apply(
    lambda x: make_line(x["COMMUNE_CENTER"], x["DCLT_CENTER"]), axis=1
)


# In[17]:


# idfData2 = idfData[idfData['IPONDI'] > 30].reset_index()
# idfData2 = idfData2[idfData2['DCLT'] != idfData2['COMMUNE']]
# idfData2 = idfData2[~((idfData2['COMMUNE'].str.contains('^75')) &
#                      (idfData2['DCLT'].str.contains('^75')))]

# idfData2 = idfData2.sort_values(['IPONDI'], ascending=False)
# idfData2['DEP'] = idfData2['DCLT'].apply(lambda x: x[:2])
# print(len(idfData2.index))
# idfData2.head(5)


# In[18]:


idfData2 = (
    idfData.query("IPONDI > 30")
    .reset_index(drop=True)
    .query("DCLT != COMMUNE")
    .query("~(COMMUNE.str.contains('^75') & DCLT.str.contains('^75'))")
    .sort_values(["IPONDI"], ascending=False)
    .assign(DEP=lambda df: df["DCLT"].apply(lambda x: x[:2]))
)
idfData2.head(5)


# In[63]:


epci


# In[61]:


import copy
from tqdm import trange

idfData5 = copy.copy(idfData2).reset_index(drop=True)
# c=0
# print( idfData5.loc[c, 'COMMUNE_CENTER'])

for i in trange(len(idfData5.index)):
    c = idfData5.loc[i, "COMMUNE_CENTER"]
    for e, geo in enumerate(list(epci["geometry"])):
        if geo.contains(c):
            idfData5.loc[i, "epci"] = e
            break


# In[19]:


import plotly.express as px
import plotly.graph_objects as go
from shapely.geometry import *


# In[20]:


idf.head(3)


# In[21]:


from tqdm import trange

# idf = com[com['insee_reg'] == '11'].reset_index()

# geo = idf.iloc[0, idf.columns.get_loc('geometry')]

list_geo = list(IDFGEO["geometry"])
list_nom = list(IDFGEO["nom"])

# list_x, list_y = [], []

layout = go.Layout(autosize=False, width=1300, height=1300)

fig = go.Figure(layout=layout)


# In[22]:


"""for g in trange(len(list_geo)):
    geo = list_geo[g]
    if type(geo) == MultiPolygon:
        for g in geo.geoms:
            xx, yy = g.exterior.coords.xy
            xx, yy = list(xx), list(yy)

            fig.add_trace(go.Scatter(
                x=xx,
                y=yy,
                mode = 'lines',
                showlegend=False,
                line=dict(color='black', width=0.5)
                ))
    else:
        xx, yy = geo.exterior.coords.xy
        xx, yy = list(xx), list(yy)

        fig.add_trace(go.Scatter(
                x=xx,
                y=yy,
                mode = 'lines',
                showlegend=False,
                line=dict(color='black', width=0.5)
                ))
                """


# In[ ]:


# In[23]:


import copy

fig2 = copy.copy(fig)

# idfData3 = idfData2[:800].reset_index(drop=True).sort_values('IPONDI', ascending=True)
idfData3 = idfData2.sort_values("IPONDI", ascending=True).reset_index(
    drop=True
)

print(len(idfData2.index))
print(len(idfData3.index))
idfData3.head(3)


# In[24]:


palette_colors = (
    sns.color_palette("Set1").as_hex()[:-2]
    + sns.color_palette("Set2").as_hex()
)


# In[25]:


# sns.color_palette("Set1").as_hex()


# In[26]:


# sns.color_palette("Set2").as_hex()


# In[27]:


list_color = [palette_colors[i] for i in range(len(palette_colors))]


# In[28]:


list_dep = ["75", "92", "94", "91", "78", "93", "95", "77"]
# palette_colors = sns.color_palette("Set1")
# list_color = ['red', 'blue', 'green', 'orange', 'brown', 'pink', 'purple', 'yellow']
# list_color = [f'rgb({c[0]}, {c[1]}, {c[2]})' for c in palette_colors[:len(list_dep)]]
# list_color


# In[29]:


from IPython.display import Markdown, display

# list_color = ['#018700', '#00acc6', '#e6a500']

display(
    Markdown(
        "<br> ".join(
            f'<span style="font-family: monospace"> DEP {list_dep[c]} <span style="color: {list_color[c]}">████████</span></span>'
            for c in range(len(list_dep))
        )
    )
)


# In[30]:


list_colors = []
for i in trange(len(idfData3)):
    dep = idfData3.iloc[i, idfData3.columns.get_loc("DEP")]
    for d, c in zip(list_dep, list_color):
        if dep == d:
            list_colors += [c]
            break


# In[31]:


idfData4 = idfData3.groupby(["DCLT", "DCLT_NAME"], as_index=False)[
    "IPONDI"
].agg("sum")
idfData4 = idfData4[~idfData4["DCLT"].str.contains("^75")].sort_values(
    "IPONDI", ascending=False
)
idfData4.head(5)


# In[32]:


idfData3


# In[33]:


import numpy as np

linestrings = list(idfData3["line"])
sizes = list(idfData3["IPONDI"])
colors = list_colors
# OldRange = (OldMax - OldMin)
# NewRange = (NewMax - NewMin)
# NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
min_sizes = min(sizes)
max_sizes = max(sizes)

sizes = [
    (s - min_sizes) * (5 - 0.1) / (max_sizes - min_sizes) + 0.1 for s in sizes
]


# In[34]:


list_of_all_arrows = []

for linestring, size, color in zip(linestrings, sizes, colors):
    x, y = linestring.xy
    x, y = list(x), list(y)

    arrow = go.layout.Annotation(
        dict(
            x=x[1],
            y=y[1],
            xref="x",
            yref="y",
            text="",
            showarrow=True,
            axref="x",
            ayref="y",
            ax=x[0],
            ay=y[0],
            arrowhead=3,
            arrowwidth=size,
            # arrowwidth=1.5,
            arrowcolor=color,
        )
    )
    list_of_all_arrows.append(arrow)

fig2 = fig2.update_layout(annotations=list_of_all_arrows)


# In[35]:


for g in trange(len(list_geo)):
    geo = list_geo[g]
    if type(geo) == MultiPolygon:
        for g in geo.geoms:
            xx, yy = g.exterior.coords.xy
            xx, yy = list(xx), list(yy)

            fig2.add_trace(
                go.Scatter(
                    x=xx,
                    y=yy,
                    mode="lines",
                    showlegend=False,
                    line=dict(color="black", width=0.5),
                )
            )
    else:
        xx, yy = geo.exterior.coords.xy
        xx, yy = list(xx), list(yy)

        fig2.add_trace(
            go.Scatter(
                x=xx,
                y=yy,
                mode="lines",
                showlegend=False,
                line=dict(color="black", width=0.5),
            )
        )


# In[36]:


# fig2.write_html("popmob.html")


# In[37]:


# fig2.write_image("popmob.png")


# In[ ]:


import kaleido

fig2.write_image("popmob.png")


# In[44]:


from PIL import Image


def resize_pix(img, pct):
    hsize = int((float(img.size[1]) * float(pct)))
    wsize = int((float(img.size[0]) * float(pct)))
    img = img.resize((wsize, hsize), Image.Resampling.LANCZOS)
    return img


img = Image.open("popmob.png").convert("RGB")
img = resize_pix(img, pct=0.5)
img


# In[39]:


# In[ ]:


# In[40]:


# from PIL import Image


# In[41]:


# display(Markdown('<br> '.join(
#    f'<span style="font-family: monospace"> DEP {list_dep[c]} <span style="color: {list_color[c]}">████████</span></span>'
#    for c in range(len(list_dep))
# )))


# In[43]:


# fig2.write_image("popmob.svg")


# In[ ]:
