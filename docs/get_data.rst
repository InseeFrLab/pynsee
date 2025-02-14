Get data
========

Get macroeconomic data
----------------------
.. autofunction:: pynsee.macrodata.get_series
    :no-index:

.. autofunction:: pynsee.macrodata.get_dataset
    :no-index:

.. autofunction:: pynsee.macrodata.get_series_title
    :no-index:


Get and analyze geographical data
---------------------------------

.. autofunction:: pynsee.geodata.get_geodata
    :no-index:

.. autoclass:: pynsee.geodata.geofrdataframe.GeoFrDataFrame
    :no-index:

    .. automethod:: get_geom
        :no-index:

    .. automethod:: transform_overseas
        :no-index:

    .. automethod:: translate
        :no-index:

    .. automethod:: zoom
        :no-index:

.. autofunction:: pynsee.geodata.transform_overseas
    :no-index:

.. autofunction:: pynsee.geodata.zoom
    :no-index:


Get local data
--------------

.. autofunction:: pynsee.localdata.get_local_data
    :no-index:

.. autofunction:: pynsee.localdata.get_population
    :no-index:

.. autofunction:: pynsee.localdata.get_old_city
    :no-index:

.. autofunction:: pynsee.localdata.get_new_city
    :no-index:

.. autofunction:: pynsee.localdata.get_ascending_area
    :no-index:

.. autofunction:: pynsee.localdata.get_descending_area
    :no-index:


Get metadata
------------

.. autofunction:: pynsee.metadata.get_definition
    :no-index:

.. autofunction:: pynsee.metadata.get_legal_entity
    :no-index:


Get sirene data
---------------

.. autofunction:: pynsee.sirene.get_sirene_data
    :no-index:

.. autofunction:: pynsee.sirene.get_sirene_relatives
    :no-index:

.. autoclass:: pynsee.sirene.sirenedataframe.SireneDataFrame
    :no-index:

    .. automethod:: get_location
        :no-index:


Get data from INSEE files
-------------------------

.. autofunction:: pynsee.download.download_file
    :no-index:

.. autofunction:: pynsee.download.get_column_metadata
    :no-index:
