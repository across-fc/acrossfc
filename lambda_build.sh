#!/usr/bin/env sh

# Create new virtualenv
python -m venv .lambda
source .lambda/bin/activate
pip install .

# Zip up all Python dependencies
curdir=$(pwd)
site_packages_path=$(python -c "import sys; print(sys.path[-1])")
cd $site_packages_path
zip -r lambda_package.zip .
cd $curdir

# Zip up handler script
mv $site_packages_path/lambda_package.zip .
zip lambda_package.zip lambda_handler.py .fcconfig

# Cleanup
rm -fr .lambda
