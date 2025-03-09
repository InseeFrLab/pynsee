.. role:: raw-html(raw)
    :format: html

Pynsee python package contains tools to easily search and download French data from INSEE and IGN APIs
======================================================================================================

.. image:: https://badge.fury.io/py/pynsee.svg
   :target: https://pypi.org/project/pynsee/
   :alt: Pypi Version

.. image:: https://img.shields.io/conda/vn/conda-forge/pynsee.svg
   :target: https://anaconda.org/conda-forge/pynsee
   :alt: Conda Forge Version

.. image:: https://codecov.io/gh/InseeFrLab/pynsee/branch/main/graph/badge.svg
   :target: https://pypi.org/project/pynsee/
   :alt: Coverage Status

.. image:: https://github.com/InseeFrLab/pynsee/actions/workflows/pkgTests.yml/badge.svg
   :target: https://github.com/InseeFrLab/pynsee/actions?query=branch%3Amaster+
   :alt: Tests Status

.. image:: https://readthedocs.org/projects/pynsee/badge/?version=latest
   :target: https://pynsee.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg
   :target: https://www.python.org/
   :alt: Python versions

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://pypi.org/project/black/
   :alt: Code formatting

.. image:: https://anaconda.org/conda-forge/pynsee/badges/license.svg
   :target: https://anaconda.org/conda-forge/pynsee
   :alt: License

.. image:: https://anaconda.org/conda-forge/pynsee/badges/latest_release_date.svg
   :target: https://anaconda.org/conda-forge/pynsee
   :alt: Latest Release Date

.. image:: https://img.shields.io/pypi/dm/pynsee
   :target: https://pypistats.org/packages/pynsee
   :alt: PyPi Downloads

:raw-html:`<br />`

``pynsee`` gives a quick access to more than 150 000 macroeconomic series,
a dozen datasets of local data, numerous sources available on `insee.fr <https://www.insee.fr>`_
as well as key metadata and SIRENE database containing data on all French companies.
Have a look at the detailed API page `portail-api.insee.fr <https://portail-api.insee.fr/>`_.

This package is a contribution to reproducible research and public data transparency.
It benefits from the developments made by teams working on APIs at INSEE and IGN.

Installation & API subscription
-------------------------------

Credentials are necessary to access SIRENE API available through ``pynsee`` by the :mod:`~pynsee.sirene` module. API credentials can be created here: `portail-api.insee.fr <https://portail-api.insee.fr/>`_. All other modules are freely accessible.

.. literalinclude:: ../README.md
    :lines: 30-44
    :language: python


Data Search and Collection Advice
---------------------------------

* **Macroeconomic data** :
   First, use :func:`~pynsee.macrodata.get_dataset_list` to search what are your datasets of interest and then get the series list with :func:`~pynsee.macrodata.get_series_list`.
   Alternatively, you can make a keyword-based search with :func:`~pynsee.macrodata.search_macrodata`, e.g. ``search_macrodata('GDP')``.
   Then, get the data with :func:`~pynsee.macrodata.get_dataset` or :func:`~pynsee.macrodata.get_series`
* **Local data** : use first :func:`~pynsee.localdata.get_local_metadata`, then get data with :func:`~pynsee.localdata.get_local_data`
* **Metadata** : e.g. function to get the classification of economic activities (Naf/Nace Rev2) :func:`~pynsee.metadata.get_activity_list`
* **Sirene (French companies database)** : use first :func:`~pynsee.sirene.get_dimension_list`, then use :func:`~pynsee.sirene.search_sirene` with dimensions as filtering variables
* **Geodata** : get the list of available geographical data with :func:`~pynsee.geodata.get_geodata_list` and then retrieve it with :func:`~pynsee.geodata.get_geodata`
* **Files on insee.fr**: get the list of available files on insee.fr with :func:`~pynsee.download.get_file_list` and then download it with :func:`~pynsee.download.download_file`

There is also the list of all modules and functions in :doc:`modules`, and more information about :doc:`utils`.

For further advice, have a look at the documentation and gallery of the `examples <https://pynsee.readthedocs.io/en/latest/examples.html>`_.

Example - Population Map
------------------------

.. image:: https://raw.githubusercontent.com/InseeFrLab/pynsee/master/docs/_static/popfrance.png


.. literalinclude:: ../README.md
    :lines: 69-129
    :language: python


How to avoid proxy issues ?
---------------------------

.. literalinclude:: ../README.md
    :lines: 136-150
    :language: python


Support
-------

Feel free to open an issue with any question about this package using <https://github.com/InseeFrLab/pynsee/issues> Github repository.

Contributing
------------

All contributions, whatever their forms, are welcome. See ``CONTRIBUTING.md``
