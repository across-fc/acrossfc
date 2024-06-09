#!/usr/bin/env zsh

# TODO: Change this into a makefile

# Create new virtualenv
python -m venv python
source python/bin/activate
pip install .

# Zip up all Python dependencies
zip -r lambda_layer.zip python

# Cleanup
rm -fr python
