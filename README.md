django-delivery
---------------

A Django Delivery app with DRF OpenAPIv3 and vue.js.


Django example Project Setup
--------------------

Prepare a virtualenv
````
pip3 install virtualenv

virtualenv -ppython3 env
source env/bin/activate
````

Get sources and install dependencies
````
git clone https://github.com/UniversitaDellaCalabria/django-delivery.git
cd django-delivery
pip install -r requirements.txt
````

Django example dev server
-------------------------

```
cd uniDelivery
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```

Manage CORS

````
pip install django-cors-headers
````

and then add it to your installed apps:

````
INSTALLED_APPS = (
    ...
    'corsheaders',
    ...
)
````

You will also need to add a middleware class to listen in on responses:

````
MIDDLEWARE_CLASSES = (
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
)

CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3030',
] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost:3030',
]
````

- Go to `https://localhost:8000/admin` and log in as the superuser you have created.
- Go to `http://localhost:8000/openapi.json` and see the API resources to the admin user (Anonymous user won't see any path)


Vue.js setup
------------

````
apt install npm

# this will embed nmp env in pyenv
pip install nodeenv
nodeenv -p

# this will install vue in the venv
npm install -g vue-cli

# put the project informations and create the vue project in the current folder
vue init webpack-simple

# install the vue project in the venv
npm install

# add a pure vue.js router
npm install vue-router --save
vue add router

# add vue-good-table
npm install --save vue-good-table

# run dev server
npm run dev
````
