# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
from __future__ import annotations

import datetime
import os

# -- Project information -----------------------------------------------------

project = "Procrastinate"
copyright = (
    f"""2019-{datetime.datetime.now().year}, Joachim Jablon, Eric Lemoine, PeopleDoc"""
)
author = "Joachim Jablon"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.programoutput",
    "sphinx_github_changelog",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]

set_type_checking_flag = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# When a word is enclosed between `backticks`, the role will automatically be
# inferred. It can be set explicitely if ambiguous.
default_role = "any"

# If we don't do that, glossary checks are case sensitive.
# https://github.com/sphinx-doc/sphinx/issues/7418
suppress_warnings = ["ref.term"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
html_static_path: list[str] = []

autoclass_content = "both"

master_doc = "index"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#e8220a",
        "color-brand-content": "#e8220a",
    },
    "dark_css_variables": {
        "color-brand-primary": "#ea9f9e",
        "color-brand-content": "#ea9f9e",
    },
    "source_repository": "https://github.com/procrastinate-org/procrastinate/",
    "source_branch": "main",
    "source_directory": "docs/",
}

html_favicon = "favicon.ico"

# -- Options for sphinx_github_changelog ---------------------------------

sphinx_github_changelog_token = os.environ.get("CHANGELOG_GITHUB_TOKEN")
