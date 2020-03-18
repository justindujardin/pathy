#!/bin/bash
set -e

#!/bin/bash
echo "Installing semantic-release requirements"
npm install 
echo "Updating build version"
npx ts-node tools/set-build-version.ts
echo "Running semantic-release"
npx semantic-release

. .env/bin/activate
git config --global user.email "justin@dujardinconsulting.com"
git config --global user.name "justindujardin"
echo "Build and publish to pypi..."
rm -rf build dist
echo "--- Install requirements"
pip install twine wheel
pip install -r requirements.txt
echo "--- Buid dists"
python setup.py sdist bdist_wheel
echo "--- Upload to PyPi"
twine upload -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} dist/*
rm -rf build dist
