# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynsee", 
    version="0.0.1",
    author="Hadrien Leclerc",
    author_email="hadrien.leclerc@insee.fr",
    description="Tools to Download Easily Data and Metadata from INSEE",
    url="https://pynsee.readthedocs.io/en/latest/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={'': ['data/*']},
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose']
)