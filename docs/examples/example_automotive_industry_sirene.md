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

# Automotive industry sites

```python
# Subscribe to api.insee.fr and get your credentials!
# Save your credentials with init_conn function :
# from pynsee.utils.init_conn import init_conn
 #init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")

# Beware : any change to the keys should be tested after having cleared the cache
# Please do : from pynsee.utils import clear_all_cache; clear_all_cache()"
```

```python
import geopandas
import pandas as pd
import numpy as np
#%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib, descartes
import matplotlib.cm as cm

from pynsee import *

# get activity list
naf5 = get_activity_list('NAF5')

# search data in SIRENE database
df = search_sirene(variable = ["activitePrincipaleEtablissement"],
                   pattern = ['29.10Z'], kind = 'siret')

# keep only businesses with more then 100 employees
df = df.loc[df['effectifsMinEtablissement'] > 100]
df = df.reset_index(drop=True)

# find latitude and longitude of all businesses
df = df.get_location()

# make geodataframe
gdf = geopandas.GeoDataFrame(df)
gdf = gdf.reset_index(drop=True)
gdf = gdf.sort_values(by=['effectifsMinEtablissement'], ascending=False)

```

```python
geodataList =  get_geodata_list()
mapdep = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:departement')

# remove overseas departments
mapdep = mapdep[~mapdep['insee_dep'].isin(['971', '972', '973', '974', '976'])]

# conversion to geopandas df
mapdepgeo = geopandas.GeoDataFrame(mapdep).set_crs("EPSG:4326")
mapdepgeo.head()
```

```python
# make cleaned labels
conditions = [gdf['denominationUniteLegale'].str.contains('RENAULT SAS'),
              gdf['denominationUniteLegale'].str.contains('PSA AUTOMOBILES'),
              gdf['denominationUniteLegale'].str.contains('[^RENAULT SAS]|[^PSA AUTOMOBILES]')]
values = ['RENAULT SAS','PSA AUTOMOBILES', 'OTHER']
gdf['label'] = np.select(conditions, values)
```

```python
# annotation
txt = 'Circles are proportionate to the minimum of the employee number range'

#plot
ax = mapdepgeo.plot(color='white', edgecolor='black', figsize = (15,7))
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
