insee-macrodata python package
=======

**Work in progress**


[![CircleCI](https://circleci.com/gh/hadrilec/py-insee_macrodata.svg?style=shield)](https://circleci.com/gh/hadrilec/py-insee_macrodata)



# Overview

The insee package contains tools to easily download data and metadata from INSEE API. 

Using the API or the SDMX queries, get the data of more than 150 000 INSEE series.

Have a look at the detailed API page with the following [link](https://api.insee.fr/catalogue/).

This package is a contribution to reproducible research and public data transparency.

## Installation & Loading

```
# Get the development version from GitHub
pip install git+https://github.com/hadrilec/py-insee_macrodata.git#egg=insee_macrodata

# Subscribe to api.insee.fr and get your credentials
os.environ['insee_key'] = "my_key"
os.environ['insee_secret'] = "my_secret_key"

```
## Examples & Tutorial

## French GDP growth rate

## Population Map

## How to avoid proxy issues ?

```
import os 
os.environ['http'] = 'http://my_proxy_server:port'
os.environ['https'] = 'http://my_proxy_server:port'
```

## Support
Feel free to contact me with any question about this package using this [e-mail address](mailto:hadrien.leclerc@insee.fr?subject=[py-package][inseeMacroData]).
