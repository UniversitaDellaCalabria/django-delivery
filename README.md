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

# run dev server
npm run dev

# install webpack bundle
# npm install webpack-bundle-tracker --save-dev
# npm install write-file-webpack-plugin --save-dev

# sass loader
# npm install --save-dev node-sass sass-loader

# ad a pure vue.js router
npm install vue-router --save
vue add router
````

````
