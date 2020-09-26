#!/bin/bash
set -e

# Make the virtualenv only if the folder doesn't exist
DIR=.env
if [ ! -d "${DIR}" ]; then
  virtualenv .env -p python3.7
fi

. .env/bin/activate
echo "Installing/updating requirements..."
pip install -r requirements.txt
echo "Installing/updating  dev requirements..."
pip install -r requirements-dev.txt
pip install -e .

