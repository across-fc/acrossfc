#!/usr/bin/env zsh

# Create new virtualenv
python -m venv python
source python/bin/activate
pip install .

# Put .fcconfig in the `python` folder so AWS Lambda will find it in PATH
cp .fcconfig python/.

# Zip up all Python dependencies
zip -r lambda_layer.zip python

# Cleanup
rm -fr python
