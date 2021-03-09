Pynsee package
=======

**Work in progress**

<br> 

 [![Build Status](https://github.com/hadrilec/pynsee/actions/workflows/pynsee-test.yml/badge.svg)](https://github.com/hadrilec/pynsee/actions) 
[![Codecov test coverage](https://codecov.io/gh/hadrilec/pynsee/branch/master/graph/badge.svg)](https://codecov.io/gh/hadrilec/pynsee?branch=master) 
 
<br> 

# Overview

The insee package contains tools to easily download data and metadata from INSEE API.
Using the API or the SDMX queries, get the data of more than 150 000 INSEE series.
Have a look at the detailed API page with the following [link](https://api.insee.fr/catalogue/).
This package is a contribution to reproducible research and public data transparency.

## Installation & Loading

```
# Get the development version from GitHub
pip install git+https://github.com/hadrilec/pynsee.git#egg=pynsee

# Subscribe to api.insee.fr and get your credentials
# Beware : any change to the keys should be test in a new python session
os.environ['insee_key'] = "my_key"
os.environ['insee_secret'] = "my_secret_key"
```
## French GDP growth rate

```
from insee_macrodata import * 
import plotly.express as px
from plotly.offline import plot

import os 
# Beware : any change to the keys should be test in a new python session
os.environ['insee_key'] = "my_insee_key"
os.environ['insee_secret'] = "my_insee_secret"

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
```
![](examples/example_gdp_picture.png)

## Population Map

## How to avoid proxy issues ?

```
import os 
os.environ['http_proxy'] = 'http://my_proxy_server:port'
os.environ['https_proxy'] = 'http://my_proxy_server:port'
```

## Support
Feel free to contact me with any question about this package using this [e-mail address](mailto:hadrien.leclerc@insee.fr?subject=[py-package][inseeMacroData]).
