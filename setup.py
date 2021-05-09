# -*- coding: utf-8 -*-

import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynsee", 
    version="0.0.1",
    author="Hadrien Leclerc",
    author_email="hadrien.leclerc@insee.fr",
    description="Tools to Easily Download Data and Metadata from INSEE APIs",
    long_description = long_description,
    url="https://pynsee.readthedocs.io/en/latest/",
     project_urls={
        'Bug Tracker': 'https://github.com/hadrilec/pynsee/issues'
    },
    packages=setuptools.find_packages(),
    license='OPEN LICENCE 2.0/LICENCE OUVERTE 2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    license_files = ('LICENSE.md',),
    install_requires=[
            "pandas>=0.24.2",
            "tqdm>=4.56.0",
            #gc, hashlib, tempfile, zipfile, math, time
            "requests>=2.25.1",
            "appdirs>=1.4.4",
            "unidecode>=1.2.0",
            "datetime>=3.5.9"],
    include_package_data=True,
    package_data={'pynsee_data': ['pynsee/macrodata/data/*',
                       'pynsee/localdata/data/*',
                       'pynsee/metadata/data/*']},
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose']
)
