#!/usr/bin/env bash

set -e
set -x

mypy pathy
flake8 pathy tests
black pathy tests --check
isort pathy tests docs_src scripts --check-only