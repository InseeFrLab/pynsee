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

# Automotive industry sites

```python
# Subscribe to api.insee.fr and get your credentials!
# Beware : any change to the keys should be tested after having cleared the cache
# Please do : from pynsee.utils import *; clear_all_cache()
# Advice : add the following lines to 'pynsee_api_credentials.py' file in your HOME directory
# to avoid running them manually
import os
os.environ['insee_key'] = "my_key"
os.environ['insee_secret'] = "my_secret_key"
```

```python

import geopandas
import pandas as pd
import numpy as np
#%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib, descartes
import matplotlib.cm as cm
from geopy.geocoders import Nominatim

from pynsee import *

# get activity list
naf5 = get_activity_list('NAF5')

# search data in SIRENE database
df = search_sirene(variable = ["activitePrincipaleEtablissement"],
                   pattern = ['29.10Z'], kind = 'siret')

# keep only businesses with more then 100 employees
df = df.loc[df['effectifsMinEtablissement'] > 100]
df = df.reset_index(drop=True)

```

```python

# find latitude and longitude of all businesses
df_location = get_location(df)
df = df.merge(df_location, on = 'siret', how='left')

# make geodataframe
gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.longitude, df.latitude))
gdf = gdf.reset_index(drop=True)
gdf = gdf.sort_values(by=['effectifsMinEtablissement'], ascending=False)

# make cleaned labels
conditions = [gdf['denominationUniteLegale'].str.contains('RENAULT SAS'),
              gdf['denominationUniteLegale'].str.contains('PSA AUTOMOBILES'),
              gdf['denominationUniteLegale'].str.contains('[^RENAULT SAS]|[^PSA AUTOMOBILES]')]
values = ['RENAULT SAS','PSA AUTOMOBILES', 'OTHER']
gdf['label'] = np.select(conditions, values)
```

```python
# get map with departments limits
mapdep = get_map('departements')

# annotation
txt = 'Circles are proportionate to the minimum of the employee number range'

#plot
ax = mapdep.plot(color='white', edgecolor='black', figsize = (15,7))
plt.title('Automotive industry sites in France')
ax.annotate(txt, xy=(-4, 41), xytext=(-4, 41))
gdf.plot(ax=ax, 
         column = 'label',
         edgecolor='white',
         markersize=gdf.effectifsMinEtablissement/5,
         legend=True,
         legend_kwds={'bbox_to_anchor': (1,1),
                       'loc':1, 'borderaxespad': 0})
plt.show()
```
