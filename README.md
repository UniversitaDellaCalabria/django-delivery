django-good-delivery
--------------------

A django app to manage delivery of goods in presence.
This application was created to manage a valid list of users for 
the delivery of an asset, such as a sim card or a 4g router. 
This application can therefore manage a stock of uniquely identifiable 
products and at the same time serve for the delivery of anonymous 
goods, such as glasses of water or bananas (without id!).


Demo project
------------

````
git clone https://github.com/UniversitaDellaCalabria/django-delivery.git
cd django-delivery
pip install -r requirements.txt

cd django_delivery
cp django_delivery/settingslocal.py.example django_delivery/settingslocal.py
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
````

Setup
-----

- Add good_delivery in settings.INSTALLED_APPS
- create your RSA keys
  ````openssl req -nodes -new -x509 -days 3650 -keyout private.key -out public.cert -subj '/CN=your.own.fqdn.com'````


Use cases and usage example
---------------------------

Todo

Tests
-----

````
./manage.py test good_delivery
````
