import os
import shutil
from pathlib import Path

def setup_docs():
    # Create docs directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Create necessary subdirectories
    (docs_dir / "_static").mkdir(exist_ok=True)
    (docs_dir / "_templates").mkdir(exist_ok=True)
    
    # Create basic documentation files
    files = {
        "index.rst": """
Welcome to DNS-Prove's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   api
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""",
        "conf.py": '''
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'DNS-Prove'
copyright = '2024, Cory Thorbeck'
author = 'Cory Thorbeck'
release = '1.2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
''',
        "Makefile": '''
# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
'''
    }
    
    for filename, content in files.items():
        with open(docs_dir / filename, 'w') as f:
            f.write(content.lstrip())

if __name__ == "__main__":
    setup_docs() 