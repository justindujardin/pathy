#!/bin/bash
set -e
echo "Activating virtualenv... (if this fails you may need to run setup.sh first)"
. .env/bin/activate
echo "Running tests..."
echo "PASSED - because they're disabled. Mock or add GCS bucket credentials"
# pytest tests --cov=gcspath

