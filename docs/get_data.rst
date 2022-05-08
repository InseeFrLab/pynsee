Get data
========

Get macroeconomic data
----------------------
.. autofunction:: pynsee.macrodata.get_series

.. autofunction:: pynsee.macrodata.get_dataset

.. autofunction:: pynsee.macrodata.get_series_title

Get geographical data
---------------------

.. autofunction:: pynsee.geodata.get_geodata

.. autoclass:: pynsee.geodata.GeoFrDataFrame.GeoFrDataFrame

    .. automethod:: get_geom

    .. automethod:: translate
    
    .. automethod:: zoom


Get local data
--------------

.. autofunction:: pynsee.localdata.get_local_data

.. autofunction:: pynsee.localdata.get_population

.. autofunction:: pynsee.localdata.get_included_area

.. autofunction:: pynsee.localdata.get_old_city

.. autofunction:: pynsee.localdata.get_new_city

Get metadata
------------

.. autofunction:: pynsee.metadata.get_definition

.. autofunction:: pynsee.metadata.get_legal_entity

Get sirene
----------

.. autofunction:: pynsee.sirene.get_sirene_data

.. autofunction:: pynsee.sirene.get_sirene_relatives

.. autoclass:: pynsee.sirene.SireneDataFrame.SireneDataFrame

    .. automethod:: get_location