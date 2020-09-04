#!/usr/bin/env bash

set -e
. .env/bin/activate

echo "========================= mypy"
mypy pathy
echo "========================= flake8"
flake8 pathy tests
echo "========================= black"
black pathy tests --check
echo "========================= pyright"
npx pyright pathy tests