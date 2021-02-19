---
title: inseeMacroData python package
output: 
  github_document
---


**Work in progress**
=======

# Overview

The insee package contains tools to easily download data and metadata from INSEE main database (BDM). 

Using embedded SDMX queries, get the data of more than 150 000 INSEE series.

Have a look at the detailed SDMX web service page with the following [link](https://www.insee.fr/en/information/2868055).

This package is a contribution to reproducible research and public data  transparency.

## Installation & Loading

```
# Get the development version from GitHub
pip install git+https://github.com/hadrilec/py-insee_macrodata.git#egg=insee_macrodata

# Get the PyPi version


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
Feel free to contact me with any question about this package using this [e-mail address](mailto:leclerc.hadrien@gmail.com?subject=[py-package][inseeMacroData]).
