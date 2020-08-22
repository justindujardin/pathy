#!/bin/bash
set -e
. .env/bin/activate
pip install codecov
python -m codecov
