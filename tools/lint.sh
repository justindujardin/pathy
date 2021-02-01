#!/usr/bin/env bash

set -e
. .env/bin/activate

echo "========================= mypy"
mypy pathy
echo "========================= flake8"
flake8 pathy
echo "========================= black"
black pathy --check
echo "========================= pyright"
npx pyright pathy