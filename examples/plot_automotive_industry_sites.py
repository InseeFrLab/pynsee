"""
Automotive industry sites
-------------------------

"""


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

# get map with departments limits
mapdep = geopandas.read_file(get_map_link('departements'))

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