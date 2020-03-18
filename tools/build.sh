#!/bin/bash
set -e
. .env/bin/activate
echo "Build python package..."
python setup.py sdist bdist_wheel
