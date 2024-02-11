#!/usr/bin/env zsh

# Create new virtualenv
python -m venv python
source python/bin/activate
pip install .

# Put .fcconfig / .gc_creds.json in the `python` folder so AWS Lambda will find it in PATH
cp .fcconfig .gc_creds.json python/.

# Zip up all Python dependencies
zip -r lambda_layer.zip python

# Cleanup
rm -fr python
