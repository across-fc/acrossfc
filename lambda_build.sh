#!/usr/bin/env zsh

# Create new virtualenv
python -m venv python
source python/bin/activate
pip install .
pip install redis

# Zip up all Python dependencies
zip -r lambda_layer.zip python

# Cleanup
rm -fr python
