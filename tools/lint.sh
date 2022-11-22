#!/usr/bin/env bash
set -e
. .env/bin/activate
echo "========================= mypy"
mypy pathy --strict-equality --disallow-untyped-calls --disallow-untyped-defs
echo "========================= flake8"
flake8 "pathy"
echo "========================= black"
black pathy --check
echo "========================= pyright"
npm i
npm run pyright
