---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---


# Poverty in Paris urban area

```python
# Subscribe to api.insee.fr and get your credentials!
# Beware : any change to the keys should be tested after having cleared the cache
# Please do : from pynsee.utils import *; clear_all_cache()
# Advice : add the following lines to 'pynsee_api_credentials.py' file in your HOME directory
# to avoid running them manually
import os
os.environ['insee_key'] = "my_key"
os.environ['insee_secret'] = "my_secret_key"

from pynsee.localdata import *

import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd

# get a list all data available : datasets and variables
metadata = get_local_metadata()

# geographic metadata
nivgeo = get_nivgeo_list()

# get geographic area list
area = get_area_list()

# get all communes in Paris urban area
areaParis = get_included_area('unitesUrbaines2020', ['00851'])

# get selected communes identifiers
code_com_paris = areaParis.code.to_list()

# get numeric values from INSEE database 
dataParis = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_com_paris)

#select poverty rate data, exclude paris commune
data_plot = dataParis.loc[dataParis.UNIT=='TP60']
data_plot = data_plot.loc[data_plot.CODEGEO!='75056']

#get communes limits
map_com = gpd.read_file(get_map_link('communes'))
map_arr_mun = gpd.read_file(get_map_link('arrondissements-municipaux'))

map_idf = pd.concat([map_com, map_arr_mun])

# merge values and geographic limits
mapparis = map_idf.merge(data_plot, how = 'right',
                     left_on = 'code', right_on = 'CODEGEO')

#plot
fig, ax = plt.subplots(1,1,figsize=[15,15])
mapparis.plot(column='OBS_VALUE', cmap=cm.viridis, 
    legend=True, ax=ax, legend_kwds={'shrink': 0.3})
ax.set_axis_off()
ax.set(title='Poverty rate in Paris urban area in 2017')
plt.show()
fig.savefig('poverty_paris_urban_area.svg',
            format='svg', dpi=1200,
            bbox_inches = 'tight',
            pad_inches = 0)

```
