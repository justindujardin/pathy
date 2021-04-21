#!/bin/bash
set -e
echo "Removing build files..."
rm -rf dist/ build/ pathy.egg-info htmlcov .test-env
