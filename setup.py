import os
from glob import glob
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

#  rm -R build/ dist/ *egg-info
#  python3 setup.py sdist
#  twine upload dist/*

setup(
    name='django-good-delivery',
    version='0.8.2',
    packages=find_packages(),
    include_package_data=True,
    license='Apache Software License',
    description="Django Good Delivery",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/UniversitaDellaCalabria/django-delivery',
    author='Giuseppe De Marco, Francesco Filicetti',
    author_email='giuseppe.demarco@unical.it, francesco.filicetti@unical.it',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
    install_requires=[
        'django>=3.0,<4.0',
        'django_ckeditor>=6.0.0',
        'django-datatables-ajax>=0.8',
        'libsass>=0.20.1',
        'django-sass-processor>=0.8.2',
        'design-django-theme>=1.4.1',
        'django-unical-bootstrap-italia>=1.0.2',
        'cryptojwt>=1.3.0'
    ],
    tests_require=[
        'pytest-django>=3.9.0',
    ]
)
