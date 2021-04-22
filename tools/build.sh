#!/bin/bash
set -e

echo "Cleaning intermediate files..."
sh tools/clean.sh

. .env/bin/activate
echo "Build python package..."
python setup.py sdist bdist_wheel
