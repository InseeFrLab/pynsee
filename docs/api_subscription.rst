.. role:: raw-html(raw)
    :format: html
    
Have a look at the official tutorial on `portail-api.insee.fr <https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/help.jag>`_

    
API Subscription Tutorial
=========================

#. Create an account on portail-api.insee.fr

#. Create an application

#. Create credentials

#. Subscribe to all APIs

#. Show your credentials

#. Save your credentials with init_conn function

.. image:: _static/myaccount.png
   :target: _static/myaccount.png
   :alt:

:raw-html:`<br />`

.. image:: _static/myapp.png
   :target: _static/myapp.png
   :alt:

:raw-html:`<br />`

.. image:: _static/mytoken.png
   :target: _static/mytoken.png
   :alt:
   
:raw-html:`<br />`

.. image:: _static/mykeys.png
   :target: _static/mykeys.png
   :alt:

:raw-html:`<br />`

.. image:: _static/mysubscription.png
   :target: _static/mysubscription.png
   :alt:
   
.. code-block:: python

   # Subscribe to api.insee.fr and get your credentials!
   # Save your credentials with init_conn function :      
   from pynsee.utils.init_conn import init_conn
   init_conn(sirene_key="my_sirene_key")

   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import clear_all_cache; clear_all_cache()