import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'PHREEQC Database Tools'
copyright = '2024, Joshua Leiper'
author = 'Joshua Leiper'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']