# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2026 RoXimn<roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("../../src"))


# Project information ----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Roman Alfaz'
copyright = '2026, RoXimn'
author = 'RoXimn'
release = '0.1.0a1'

# General configuration --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx_rtd_theme",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
