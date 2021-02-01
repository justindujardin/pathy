#!/bin/bash
set -e
echo "Activating virtualenv... (if this fails you may need to run setup.sh first)"
. .env/bin/activate
echo "Running tests..."
pytest pathy/tests --cov=pathy

