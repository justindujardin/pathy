#!/bin/bash
set -e
uv run pip install codecov
uv run python -m codecov
