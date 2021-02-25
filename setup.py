# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 14:41:14 2020

@author: eurhope
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="insee-macrodata", 
    version="0.0.1",
    author="Hadrien Leclerc",
    author_email="leclerc.hadrien@gmail.com",
    description="Tools to Download Easily Data and Metadata from INSEE BDM Database",
    url="",
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