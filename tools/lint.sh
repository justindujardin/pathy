#!/usr/bin/env bash

set -e
. .env/bin/activate

mypy pathy
flake8 pathy tests
black pathy tests --check
