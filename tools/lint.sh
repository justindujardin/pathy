#!/usr/bin/env bash
set -e
echo "========================= mypy"
uv run mypy pathy
echo "========================= flake8"
uv run flake8 pathy
echo "========================= black"
uv run black pathy --check
