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
sys.path.insert(0, os.path.abspath('../esrpoise'))

# Get version number
exec(open('../esrpoise/_version.py').read())


# -- Project information -----------------------------------------------------

project = 'ESR-POISE'
copyright = '2022, Jean-Baptiste Verstraete, Jonathan Yong, Mohammadali Foroozandeh'
author = 'Jean-Baptiste Verstraete, Jonathan Yong, Mohammadali Foroozandeh'

# The full version, including alpha/beta/rc tags
# release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.autosectionlabel"
]

autodoc_member_order = 'bysource'
autodoc_typehints = 'none'

rst_prolog = """
.. |version| replace:: {}
.. |Path| replace:: :class:`Path <pathlib.Path>`
.. |ndarray| replace:: :class:`ndarray <numpy.ndarray>`
.. |v| replace:: |br| |vspace|
.. |br| raw:: html

   <br />

.. |vspace| raw:: latex

   \\vspace{{5mm}}
""".format(__version__)


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_theme_options = {
    "page_width": "1000px",
    "sidebar_width": "250px",
}

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    "fontpkg": "",
    "fncychap": "",
    "preamble": r"""
        \setkeys{Gin}{width=0.6\linewidth}
        \usepackage{charter}
        \usepackage[defaultsans]{lato}
        \usepackage{inconsolata}
        """,
    "extraclassoptions": "openany",
    "printindex": "\\def\\twocolumn[#1]{#1}\\printindex",
}