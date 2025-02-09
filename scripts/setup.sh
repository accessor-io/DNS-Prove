#!/bin/bash

# Install dependencies
pip install -e ".[dev,docs]"

# Create documentation structure
python scripts/setup_docs.py

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit"
fi

echo "Setup complete! You can now build the documentation with: cd docs && make html" 