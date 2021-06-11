#!/bin/sh
set -e

folders="api tests"

set -x

# stop the build if there are Python syntax errors or undefined names
flake8 $folders --count --show-source --statistics --select=E9,F63,F7,F82
# exit-zero treats all errors as warnings
flake8 $folders --count --exit-zero --statistics

# check formatting with black
black $folders --check --line-length 100

# check import ordering with isort
isort $folders --check-only
