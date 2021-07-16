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


## Population Pyramid

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
pd.options.mode.chained_assignment = None 
#%matplotlib inline
import matplotlib.pyplot as plt

metadata = get_local_metadata()

data = get_insee_local(dataset_version='GEO2020RP2017',
                       variables = 'SEXE-AGED100',
                       nivgeo = 'FE',
                       geocodes=['1'])

dataM = data[(data.SEXE == '1') & (data.AGED100 != 'ENS')]
dataF = data[(data.SEXE == '2') & (data.AGED100 != 'ENS')]

dataF['OBS_VALUE'] = dataF['OBS_VALUE'].apply(lambda x: x * -1)

# define plot
y = range(0, len(dataM))
x_male = dataM['OBS_VALUE']
x_female = dataM['OBS_VALUE']

#define plot parameters
fig, axes = plt.subplots(ncols=2, sharey=True, figsize=(12, 5))
fig.suptitle("Population Pyramid in France in 2017", fontweight='bold')
fig.tight_layout(pad = 2)
#define male and female bars
axes[0].barh(y, x_male, align='center', color='blue')
axes[0].set(title='Males')
axes[1].barh(y, x_female, align='center', color='red')
axes[1].set(title='Females')
axes[0].invert_xaxis()



```
