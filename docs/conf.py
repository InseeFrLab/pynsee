# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys

os.chdir("../")
sys.path.insert(0, os.path.abspath("./"))


import pynsee


# -- Project information -----------------------------------------------------

project = "pynsee"
copyright = "2021, INSEE"
author = "Hadrien Leclerc"

# The short X.Y version
version = re.match(r"\d+\.\d+\.\d+", pynsee.__version__).group()

# The full version, including alpha/beta/rc tags
release = pynsee.__version__

version_selector = True


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "nbsphinx",
    "sphinxcontrib.rsvgconverter",
    "sphinx.ext.mathjax",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx_gallery.load_style",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

# 'sphinx_gallery.gen_gallery'
# "sphinxcontrib.rsvgconverter",
# 'sphinx.ext.imgconverter',

# sphinx_gallery_conf = {
#      'examples_dirs': '../examples',   # path to your example scripts
#      'gallery_dirs': 'auto_examples',  # path to where to save gallery generated output
# }

nbsphinx_thumbnails = {
    "examples/example_commute_paris": "_static/commute_paris.png",
    "examples/example_gdp_growth_rate_yoy": "_static/gdp_growth_rate_yoy.png",
    "examples/example_poverty_paris_urban_area": "_static/poverty_paris_urban_area.png",
    "examples/example_poverty_marseille": "_static/poverty_marseille.png",
    "examples/example_doctors_idf": "_static/doctors_paris.png",
    "examples/example_insee_premises_sirene": "_static/insee_premises.png",
    "examples/example_presidential_election2022": "_static/presidential_election2022.png",
    "examples/example_empl_sector_dep": "_static/empl_sector_dep.png",
    "examples/example_automotive_industry_sirene": "_static/automotive_industry_sirene.png",
    "examples/example_population_map_com": "_static/popfrance.png",
    "examples/example_population_pyramid": "_static/population_pyramid.png",
    "examples/example_deaths_births": "_static/deaths_births.png",
    "examples/example_inflation_yoy": "_static/inflation_yoy.png",
    "examples/example_inflation_contribution": "_static/inflation_contribution.png",
    "examples/example_cadre_iris_idf": "_static/upper_middle_class_worker_idf.png",
    "examples/example_marie_firstname": "_static/firstname.png",
    "examples/example_rp_logement_2017": "_static/housing.png",
}


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {"display_version": True}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# exclude from copy button code snippet
copybutton_prompt_text = ">>> "


# full screen use
def setup(app):
    app.add_css_file("my_theme.css")


# -- Options for extensions --------------------------------------------------

napoleon_use_admonition_for_notes = True
napoleon_use_rtype = False

# links to GeoPandas' documentation
intersphinx_mapping = {
    "gpd": ("https://geopandas.org/en/stable/", None),
    "pd": ("https://pandas.pydata.org/docs", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}
