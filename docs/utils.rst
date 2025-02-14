Configuration and utilities
===========================

Utility functions
-----------------

.. autofunction:: pynsee.utils.init_conn
    :noindex:

.. autofunction:: pynsee.utils.clear_all_cache
    :noindex:


Configuring the library's behavior
----------------------------------

``pynsee`` can also be configured via the following environment variables:

- ``SIRENE_KEY`` takes precedence over the one that may be save in the config file
- ``HTTP_PROXY`` and ``HTTPS_PROXY`` also override config proxy
- ``PYNSEE_SILENT_MODE`` silences all logging information about cached files
