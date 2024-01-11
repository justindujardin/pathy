#!/bin/bash
set -e

echo "Cleaning intermediate files..."
sh tools/clean.sh

. .env/bin/activate
echo "Build python package..."
# .env/bin/python setup.py sdist bdist_wheel
.env/bin/pip wheel . -w dist
