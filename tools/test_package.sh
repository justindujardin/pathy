#!/bin/bash
set -e

# Make the virtualenv only if the folder doesn't exist
DIR=.test-env
if [ ! -d "${DIR}" ]; then
    pip install virtualenv
    python -m virtualenv .test-env -p python3
fi

. .test-env/bin/activate

WHEEL=`find ./dist -iname '*.whl' | head -n 1`

pip install "${WHEEL}[test]"
echo " === Running tests WITHOUT package extras installed..."
python -m pytest --pyargs pathy._tests --cov=pathy


pip install "${WHEEL}[all]"
echo " === Running tests WITH package extras installed..."
python -m pytest --pyargs pathy._tests --cov=pathy --cov-append