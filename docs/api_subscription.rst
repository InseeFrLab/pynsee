.. role:: raw-html(raw)
    :format: html

Have a look at the official tutorial on `api.insee.fr <https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/help.jag>`_


API Subscription Tutorial
=========================

#. Create an account on api.insee.fr

#. Create an application

#. Create credentials

#. Subscribe to all APIs

#. Show your credentials

#. Save your credentials with init_conn function

.. image:: _static/myaccount.png
   :target: _static/myaccount.png
   :alt: Click on "Créer son compte", which means "create an account", in French, when on https://api.insee.fr

:raw-html:`<br />`

.. image:: _static/myapp.png
   :target: _static/myapp.png
   :alt: Once logged, click on "Mes applications" (my apps), then on "Ajouter une application" '(add an app).

:raw-html:`<br />`

.. image:: _static/mytoken.png
   :target: _static/mytoken.png
   :alt: Select "Clefs et jetons d'accès" (keys and tokens) and click on "Générer les clefs" (generate keys) to create your credentials.

:raw-html:`<br />`

.. image:: _static/mykeys.png
   :target: _static/mykeys.png
   :alt: Then click on "Montrer les clefs" (show keys) and copy these for use in the init_con function.

:raw-html:`<br />`

.. image:: _static/mysubscription.png
   :target: _static/mysubscription.png
   :alt: Use the newly created application to subscribe to all relevant APIs via "Les APIs de l'INSEE", then selecting each API (B, L, M, S), select the new applications in "Applications", and click "Souscrire" (subscribe).

.. code-block:: python

   # Subscribe to api.insee.fr and get your credentials!
   # Save your credentials with init_conn function :
   from pynsee.utils.init_conn import init_conn
   init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")

   # Beware : any change to the keys should be tested after having cleared the cache
   # Please do : from pynsee.utils import clear_all_cache; clear_all_cache()
