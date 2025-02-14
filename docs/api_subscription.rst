.. role:: raw-html(raw)
    :format: html

Have a look at the official tutorial on `portail-api.insee.fr <https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/help.jag>`_


API Subscription Tutorial
=========================

.. note::

    This is only necessary if you want to access data from the SIRENE API, all other APIs are now freely accessible.


Steps to access the SIRENE API via ``pynsee``
---------------------------------------------

#. Create an account on portail-api.insee.fr

#. Create an application

#. Go to catalog, click on SIRENE and subscribe with you newly created application

#. Copy the API key

#. Save your credentials with init_conn function

.. code-block:: python

   # Subscribe to api.insee.fr and get your credentials!
   # Save your credentials with init_conn function :
       from pynsee.utils.init_conn import init_conn
       init_conn(sirene_key="my_sirene_key")

       # Beware: any change to the keys should be tested after having cleared the cache
       # Please do: from pynsee.utils import clear_all_cache; clear_all_cache()

.. note::

    For existing subscriptions, you can always find the key again by going in "Applications", clicking on the application name, then on the "Souscriptions" tab, and finally on "API Sirene": it appears on the right under "Clés d'API"


Images of the subscription steps
--------------------------------

.. image:: _static/myaccount.png
   :target: _static/myaccount.png
   :alt: First click on "Se Connecter", then choose "Connexion pour les externes" if you do not work for INSEE and create an account or log in.

:raw-html:`<br />`

.. image:: _static/myapp.png
   :target: _static/myapp.png
   :alt: Once logged in, click on "Applications", then on "Créer une app" and create the application.

:raw-html:`<br />`

.. image:: _static/sirene.png
   :target: _static/sirene.png
   :alt: Once the app is created, click on "Catalogue", then on "API Sirene".

:raw-html:`<br />`

.. image:: _static/subscribe.png
   :target: _static/subscribe.png
   :alt: Then click on "Souscrire", click "Suivant", then select you application, click "Suivant" and validate the subscription.

:raw-html:`<br />`

.. image:: _static/mytoken.png
   :target: _static/mytoken.png
   :alt: The token appears after "Voici votre clé personnelle pour accéder à l'API"; click on the clipboard icon to copy it.
