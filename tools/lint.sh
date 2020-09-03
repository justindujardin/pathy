#!/usr/bin/env bash

set -e
set -x

mypy pathy
flake8 pathy tests
black pathy tests --check
