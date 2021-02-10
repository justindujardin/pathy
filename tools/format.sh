#!/bin/sh -e
. .env/bin/activate

# Sort imports one per line, so autoflake can remove unused imports
isort pathy --force-single-line-imports
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place pathy --exclude=__init__.py
isort pathy
black pathy 