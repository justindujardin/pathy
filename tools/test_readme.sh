#!/bin/bash
set -e
. .env/bin/activate
python tools/test_readme.py README.md
