.. role:: raw-html-m2r(raw)
   :format: html

Introduction to pynsee package
==============================

**Work in progress**

.. image:: https://github.com/InseeFrLab/Py-Insee-Data/actions/workflows/master.yml/badge.svg
   :target: https://github.com/InseeFrLab/Py-Insee-Data/actions
   :alt: Build Status

.. image:: https://codecov.io/gh/InseeFrLab/pynsee/branch/master/graph/badge.svg?token=TO96FMWRHK
   :target: https://codecov.io/gh/InseeFrLab/Py-Insee-Data?branch=master
   :alt: Codecov test coverage

.. image:: https://readthedocs.org/projects/pynsee/badge/?version=latest
   :target: https://pynsee.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

``pynsee`` package contains tools to easily download data and metadata from INSEE APIs and website.

``pynsee`` gives a quick access to more than 150 000 macroeconomic series,
a dozen datasets of local data, numerous sources available on <https://www.insee.fr>
as well as key metadata and SIRENE database containing data on all French companies.
Have a look at the detailed API page with the following `link <https://api.insee.fr/catalogue/>`_.
This package is a contribution to reproducible research and public data transparency. 
It benefits from the developments made by INSEE's teams working on APIs.

Installation & API subscription
-------------------------------

The dataset available on <https://www.insee.fr> do not require authentication.
Credentials are necessary to access some of the APIs available on `pynsee`. 
API credentials can be created <https://api.insee.fr/catalogue/>

.. code-block:: python

   # Get the development version from GitHub
   # git clone https://github.com/InseeFrLab/Py-Insee-Data.git
   # cd Py-Insee-Data
   # pip install .

   # Subscribe to api.insee.fr and get your credentials!
   # Save your credentials with init_conn function :      
   from pynsee.utils.init_conn import init_conn
   init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")

   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import clear_all_cache; clear_all_cache()

Data Search and Collection Advice
---------------------------------

Regarding APIs: 

* **Macroeconomic data** :
   First, use ``get_dataset_list`` to search first among the datasets.
   Alternatively, you can make a keyword-based search with ``search_macrodata``, e.g. ``search_macrodata('GDP')``.
   Then, get the data with ``get_dataset`` or ``get_series``
* **Local data** : use first ``get_local_metadata``, then get data with ``get_local_data``
* **Metadata** : e.g. function to get the classification of economic activities (Naf/Nace Rev2) ``get_activity_list`` 
* **Sirene (French companies database)** : use first ``get_all_columns``, and then use ``search_sirene``

Regarding data that can be downloaded directly from the website, the main entry point is ``telechargerDonnees``:

.. code-block:: python

   from pynsee.download import telechargerDonnees
   df = telechargerDonnees("FILOSOFI_COM", date = "2015")


For further advice, have a look at the documentation and the examples


French GDP growth rate
----------------------

Below is an example to easily download and display French GDP growth series

.. image:: https://raw.githubusercontent.com/InseeFrLab/Py-Insee-Data/master/docs/examples/pictures/example_gdp_picture.png?token=AP32AXOVNXK5LWKM4OJ5THDAZRHZK

.. mdinclude:: examples/example_gdp_growth_rate_yoy.md

Poverty in Paris urban area
---------------------------

Below is an example to easily download and represent French GDP growth series

.. image:: https://raw.githubusercontent.com/InseeFrLab/Py-Insee-Data/master/docs/examples/pictures/poverty_paris_urban_area.svg?token=AP32AXNFHNAH2NEK2LKWENTAZO7YY

.. mdinclude:: examples/example_poverty_paris_urban_area.md

How to avoid proxy issues ?
---------------------------

.. code-block:: python

   # Use the proxy_server argument of the init_conn function to change the proxy server address   
   from pynsee.utils.init_conn import init_conn
   init_conn(insee_key="my_insee_key",
             insee_secret="my_insee_secret",
             proxy_server="http://my_proxy_server:port")

   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import *; clear_all_cache()

Support
-------

Feel free to open an issue with any question about this package using <https://github.com/InseeFrLab/Py-Insee-Data> Github repository.

Contributing
------------

All contributions, whatever their forms, are welcome. See ``CONTRIBUTING.md``
