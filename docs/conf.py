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

import datetime
import os
import pathlib
import sys
from typing import List

# -- Project information -----------------------------------------------------

project = "procrastinate"
copyright = f"{datetime.datetime.now().year}, Peopledoc"
author = "Peopledoc"


# -- General configuration ---------------------------------------------------
sys.path.append(str(pathlib.Path("sphinxext").absolute()))

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.programoutput",
    "changelog",
]
try:
    import sphinxcontrib.spelling  # noqa
except ImportError:
    pass
else:
    extensions.append("sphinxcontrib.spelling")

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

# -- Spell check -------------------------------------------------------------

spelling_word_list_filename = "spelling_wordlist.txt"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
html_static_path: List[str] = []

autoclass_content = "both"

master_doc = "index"

html_theme_options = {
    "description": "Python/PostgreSQL task processing library",
    "sidebar_width": "235px",
    "github_user": "peopledoc",
    "github_repo": "procrastinate",
    "badge_branch": "master",
    "codecov_button": True,
    "github_banner": True,
    "github_button": True,
    "travis_button": True,
}

changelog_github_token = os.environ.get("CHANGELOG_GITHUB_TOKEN")
