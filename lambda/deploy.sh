#!/usr/bin/env zsh

# TODO: Change this into a makefile

# Create new virtualenv
BUILD_ENV=lambda_build_env
python -m venv $BUILD_ENV
source $BUILD_ENV/bin/activate
pip install .

# Zip up all Python dependencies, publish to S3
TIMESTAMP=$(date +%Y_%m_%d_%H_%M_%S)
LAYER_FILENAME=lambda_layer_${TIMESTAMP}.zip
zip -r $LAYER_FILENAME $BUILD_ENV
aws s3 cp $LAYER_FILENAME s3://acrossfc-lambda-layers/$LAYER_FILENAME

# Cleanup
rm -fr $BUILD_ENV
rm $LAYER_FILENAME
