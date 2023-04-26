
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

