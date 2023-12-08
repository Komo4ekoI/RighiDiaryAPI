import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('.'))

project = 'RighiDiary'
author = 'Teliatnyk Vadym'

html_theme_options = {
    'description': 'Obtaining data from the electronic register of the lyceum "Liceo Scientifico A. Righi"',
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

master_doc = 'index'

source_suffix = ['.rst', '.md']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

source_dir = os.path.join(os.path.abspath('..'), 'src')
sys.path.insert(0, source_dir)
