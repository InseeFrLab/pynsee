.. role:: raw-html-m2r(raw)
   :format: html

Introduction to pynsee package
==============================

**Work in progress**

.. image:: https://github.com/InseeFrLab/Py-Insee-Data/actions/workflows/master.yml/badge.svg
   :target: https://github.com/InseeFrLab/Py-Insee-Data/actions
   :alt: Build Status

.. image:: https://codecov.io/gh/InseeFrLab/Py-Insee-Data/branch/master/graph/badge.svg?token=TO96FMWRHK
   :target: https://codecov.io/gh/InseeFrLab/Py-Insee-Data?branch=master
   :alt: Codecov test coverage

.. image:: https://readthedocs.org/projects/pynsee/badge/?version=latest
   :target: https://pynsee.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

The pynsee package contains tools to easily download data and metadata from INSEE APIs.
Pynsee gives a quick access to more than 150 000 macroeconomic series,
a dozen datasets of local data, key metadata and SIRENE database containing data on all French companies.
Have a look at the detailed API page with the following `link <https://api.insee.fr/catalogue/>`_.
This package is a contribution to reproducible research and public data transparency. 
It benefits from the developments made by INSEE's teams working on APIs.

Installation & Loading
----------------------

.. code-block:: python

   # Get the development version from GitHub
   # pip install git+https://github.com/InseeFrLab/Py-Insee-Data.git#egg=pynsee

   # Subscribe to api.insee.fr and get your credentials!
   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import *; clear_all_cache()
   # Advice : add the following lines to 'pynsee_api_credentials.py' file in your HOME directory
   # to avoid running them manually
   import os
   os.environ['insee_key'] = "my_key"
   os.environ['insee_secret'] = "my_secret_key"


French GDP growth rate
----------------------

.. image:: https://raw.githubusercontent.com/InseeFrLab/Py-Insee-Data/master/docs/examples/pictures/example_gdp_picture.png?token=AP32AXOVNXK5LWKM4OJ5THDAZRHZK
.. code-block:: python

   from pynsee.macrodata import *
  
   import pandas as pd
   import matplotlib.ticker as ticker
   import matplotlib.pyplot as plt

   # Subscribe to api.insee.fr and get your credentials!
   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import *; clear_all_cache()
   # Advice : add the following lines to 'pynsee_api_credentials.py' file in your HOME directory
   # to avoid running them manually
   import os
   os.environ['insee_key'] = "my_insee_key"
   os.environ['insee_secret'] = "my_insee_secret"

   # get series key (idbank), for Gross domestic product balance
   id = get_series_list("CNT-2014-PIB-EQB-RF")

   id = id.loc[(id.FREQ == "T") &
               (id.OPERATION == "PIB") &
               (id.NATURE == "TAUX") &
               (id.CORRECTION == "CVS-CJO")]

   data = get_series(id.IDBANK)

   data = split_title(df = data, n_split=2)

   # define plot
   ax = data.plot(kind='bar', x="TIME_PERIOD", stacked=True, y="OBS_VALUE", figsize=(15,5))
   #add title
   plt.title("French GDP growth rate, quarter-on-quarter, sa-wda")
   # customize x-axis tickers
   ticklabels = ['']*len(data.TIME_PERIOD)
   ticklabels[::12] = [item for item in data.TIME_PERIOD[::12]]
   ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
   plt.gcf().autofmt_xdate()
   #remove legend
   ax.get_legend().remove()
   #remove x-axistitle
   ax.xaxis.label.set_visible(False)
   plt.show()

Poverty in Paris urban area
---------------------------

.. image:: https://raw.githubusercontent.com/InseeFrLab/Py-Insee-Data/master/docs/examples/pictures/poverty_paris_urban_area.svg?token=AP32AXNFHNAH2NEK2LKWENTAZO7YY

.. code-block:: python
   
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
   dataParis = get_local_data(dataset_version='GEO2020FILO2017',
                          variables =  'INDICS_FILO_DISP_DET',
                          nivgeo = 'COM',
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


How to avoid proxy issues ?
---------------------------

.. code-block:: python

   # Advice : add the following lines to 'pynsee_api_credentials.py' file in your HOME directory
   # to avoid running them manually
   import os
   os.environ['http_proxy'] = 'http://my_proxy_server:port'
   os.environ['https_proxy'] = 'http://my_proxy_server:port'


Support
-------

Feel free to contact me with any question about this package using this `e-mail address <mailto:hadrien.leclerc@insee.fr?subject=[pynsee]>`_.

