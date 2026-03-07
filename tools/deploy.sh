#!/bin/bash
set -e

echo "Installing semantic-release requirements"
npm install
echo "Updating build version"
npx ts-node -O '{"module": "es2020", "esModuleInterop":true}' tools/ci-set-build-version.ts
echo "Running semantic-release"
npx semantic-release

echo "Build and publish to pypi..."
rm -rf dist
echo "--- Build dists"
uv build
echo "--- Upload to PyPi"
uv run twine upload -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} dist/* || true
rm -rf dist
