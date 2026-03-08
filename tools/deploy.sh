#!/bin/bash
set -e

echo "Running semantic-release (bump version, changelog, commit, tag, push)..."
# semantic-release version exits 0 if a release was made, non-zero otherwise.
# build_command in pyproject.toml runs "uv build" automatically.
if uv run semantic-release version; then
    echo "Publishing to PyPI..."
    uv run twine upload -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} dist/* || true
    rm -rf dist

    echo "Publishing dist artifacts to GitHub release..."
    uv run semantic-release publish
else
    echo "No release needed (no qualifying commits since last release)."
fi
