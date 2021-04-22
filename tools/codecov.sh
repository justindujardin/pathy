#!/bin/bash
set -e
. .env/bin/activate
pip install codecov coverage
python -m coverage combine
python -m codecov
