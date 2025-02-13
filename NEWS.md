# pynsee 0.2.0

**Breaking changes**

The INSEE APIs were changed, including

* new API portal: portail-api.insee.fr
* no token generation is needed for all APIs except SIRENE
* for SIRENE API, it is now provided via the ``sirene_key`` argument in ``init_conn``.

**New features**

* ``GeoFrDataFrame`` inherits from ``geopandas.GeoDataFrame`` so you can use all the included methods directly on it (#246)
* the tranlation and zoom of overseas department has be renamed ``transform_overseas``, ``translate`` is still available but deprecated.
* the configuration file is no longer stored in the middle of the home directory (#210)

**Documentation** (# #250 #251)

* updated examples and user guides
* internal links for functions and classes
* link to pandas/geopandas/pyproj and request documentations

**Under the hood**

* use data from Melodi api (#229)
* backend function update in the utils module + sirene functions update
* cleanup of temporary files handling (#206)
* subsequent doc and test update
* all cached data is now saved as parquet for faster read/write operations (#199 #208 #)
* switch to multithreading instead of multiprocessing (#216)
* move to pyproject.toml only (#243)
* fix tests (many commits)

# pynsee 0.1.8

* sirene module compatible with SIRENE API v3.11
* geodata module compatible with the new IGN's geoplatform
* data cached in parquet files thanks to a new decorator used across modules
* fixes in the docs/examples
* macroeconomic series list can be retrieved even if it is zipped twice
* macroeconomic series can be used even if INSEE adds .TRUE or .FALSE at the end of the identifier
* if RSS feed is failing, the get_last_release returns a warning and not an error
* conda forge releases streamlined

# pynsee 0.1.7

* README.rst deleted and README.md included in package distribution file
* python version badge update in readme

# pynsee 0.1.6

* fix to cope with the double zipping of macroeconomic metadata file containing time series identifiers
* changes in geodata module to switch to the new IGN geoplatform
* tests performed on python 3.8-3.11
* new example in doc gallery on mobility in Paris region + example fixes
* package catches error 429 (request limit on api.insee.fr) and then sleeps

# pynsee 0.1.5

* shapely>= 1.8.0 defined in both setup.py and requirements

# pynsee 0.1.4

* translate method: bug fix due to IGN data flow discontinuity
* package compatible with shapely 2.0 + deprecation warnings removed

# pynsee 0.1.3

* get_area_list provides list of communes, departements etc.
* get_included_area is deprecated, get_descending_area should be used instead
* get_ascending_area returns admnistrative areas containing the area provided as input
* geopandas bugfix: crs is no longer contained in 'crs' column but in 'crsCoord'
* init_conn arguments names changed + proxy server settings have been tested
* error handling messages improved in _request_insee function
* GEOlatest\<datasetName\>latest used as input of get_local_data returns the latest data available
* pull requests use secrets from repo
* pathlib dependency removed + openpyxl<=3.1.0
* doc update

# pynsee 0.1.2

* license change from open license 2.0 to MIT license

# pynsee 0.1.1

* idbank file download from both French and English webpages on insee.fr
* internal idbank list update
* readme update

# pynsee 0.1.0

* tools to search and download data from INSEE APIs : BDM, LocalData, MetaData, SIRENE
* automatic token generator for api.insee.fr from user's credentials saved locally
* pynsee.download module gives access to more than 1200 stored files on insee.fr
* tools to search and download geographical data from IGN API : administrative limits
* GeoFrDataFrame class with dedicated modules to manipulate overseas departements data
* SireneDataFrame class with a module locating entities thanks to OpenStreetMap
* data is usually saved locally to enhance user experience
* data stored internally in the package (used mostly as backups):
    * BDM series list
    * BDM datasets list
    * local metadata
    * activity classification (naf rev2 2008)
    * list of definitions
    * list of files on insee.fr
    * full documentation made with docstring and hosted by ReadTheDocs
    * hands-on examples covering all modules displayed in the documentation
    * test coverage >90%
