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
import sys
import sphinx_copybutton
import sphinx_rtd_theme
import m2r2
import sphinxcontrib

# import rinoh
os.chdir('../')
sys.path.insert(0, os.path.abspath('./'))


# -- Project information -----------------------------------------------------

project = 'pynsee'
copyright = '2021, INSEE'
author = 'Hadrien Leclerc'

# The short X.Y version
version = '0.0.1'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
     "sphinx_rtd_theme",     
     'sphinx.ext.autodoc',
     'sphinx_copybutton',
     'nbsphinx', 
     "m2r2",
     'sphinx.ext.mathjax',  
     "sphinxcontrib.rsvgconverter",
     #'sphinx.ext.imgconverter',   
     'IPython.sphinxext.ipython_console_highlighting',
     # 'sphinx_gallery.gen_gallery'
]


# sphinx_gallery_conf = {
#      'examples_dirs': '../examples',   # path to your example scripts
#      'gallery_dirs': 'auto_examples',  # path to where to save gallery generated output
# }


# 'm2r2',
# "rinoh.frontend.sphinx"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store','**.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# html_static_path = []

# exclude from copy button code snippet
copybutton_prompt_text = ">>> "

# full screen use
def setup(app):
    app.add_css_file('my_theme.css')

# include alos md doc
source_suffix = ['.rst'] # , '.md'