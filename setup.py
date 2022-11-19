# -*- coding: utf-8 -*-

import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynsee",
    version="0.1.1",
    author="Hadrien Leclerc, Lino Galiana",
    author_email="leclerc.hadrien@gmail.com",
    description="Tools to Easily Search and Download French Data From INSEE and IGN APIs",
    long_description=long_description,
    url="https://pynsee.readthedocs.io/en/latest/",
    project_urls={
        'Bug Tracker': 'https://github.com/InseeFrLab/Py-Insee-Data/issues'
    },
    packages=setuptools.find_packages(),
    license='OPEN LICENCE 2.0/LICENCE OUVERTE 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    license_files=('LICENSE.md',),
    install_requires=[
            "pandas>=0.24.2",
            "tqdm>=4.56.0",
            "requests>=2.23",
            "appdirs>=1.4.4",
            "unidecode>=1.1.0",
            "shapely>=1.8.0,<2.0",
            "urllib3",
            "pathlib"],
    extras_require={
        'full': ['openpyxl', "xlrd>=2.0.1"]
    },
    package_data={
        "": ["*.zip"]},
    python_requires='>=3.7',
    test_suite='nose.collector',
    tests_require=['nose']
)
