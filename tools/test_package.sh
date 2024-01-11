#!/bin/bash
set -e

# Make the virtualenv only if the folder doesn't exist
DIR=.test-env
if [ ! -d "${DIR}" ]; then
    pip install virtualenv
    python -m virtualenv .test-env -p python3
fi

WHEEL=`find ./dist -iname 'pathy-*.whl' | head -n 1`

.test-env/bin/pip install "${WHEEL}[test]"
echo " === Running tests WITHOUT package extras installed..."
.test-env/bin/python -m pytest --pyargs pathy._tests --cov=pathy


.test-env/bin/pip install "${WHEEL}[all]"
echo " === Running tests WITH package extras installed..."
.test-env/bin/python -m pytest --pyargs pathy._tests --cov=pathy --cov-append