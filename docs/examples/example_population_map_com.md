---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region tags=[] -->
# Population Map by Communes
<!-- #endregion -->

```python
from pynsee.geodata import *

import geopandas as gpd
import pandas as pd
from pandas.api.types import CategoricalDtype
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import descartes
```

```python
# get geographical data list
geodata_list = get_geodata_list()
# get departments geographical limits
com = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:commune')
```

```python
geodata_list.head()
```

```python
com.head()
```

```python
# remove overseas departments
comfrm = com[~com['insee_dep'].isin(['971', '972', '973', '974', '976'])]
```

```python
map = gpd.GeoDataFrame(comfrm).set_crs("EPSG:4326")
map['REF_AREA'] = 'D' + map['insee_dep']

map = map.to_crs(epsg=3035)
map["area"] = map['geometry'].area / 10**6
map = map.to_crs(epsg=4326)

map['density'] = map['population'] / map["area"]
```

```python

map.loc[map.density < 40, 'range'] = "< 40"
map.loc[map.density >= 20000, 'range'] = "> 20 000"

density_ranges = [40, 50, 70, 100, 120, 160, 200, 240, 260, 410, 600, 1000, 5000, 20000]
list_ranges = []
list_ranges.append( "< 40")

for i in range(len(density_ranges)-1):
    min = density_ranges[i]
    max = density_ranges[i+1]
    range_string = "[{}, {}[".format(min, max)
    map.loc[(map.density >= min) & (map.density < max), 'range'] = range_string
    list_ranges.append(range_string)

list_ranges.append("> 20 000")

map['range'] = map['range'].astype( CategoricalDtype(categories=list_ranges, ordered=True))

fig, ax = plt.subplots(1,1,figsize=[10,10])
map.plot(column='range', cmap=cm.viridis, 
    legend=True, ax=ax,
    legend_kwds={'bbox_to_anchor': (1.1, 0.8),
                 'title':'density per km2'})
ax.set_axis_off()
ax.set(title='Distribution of population in metropolitan France')
plt.show()
```
