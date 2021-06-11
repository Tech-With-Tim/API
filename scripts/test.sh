#!/bin/sh
set -e

lint=true

# no linitng if -n or --no-lint flag
for arg in "$@"
do
    if [ "$arg" == "-n" ] || [ "$arg" == "--no-lint" ]; then
        lint=false
    fi
done

if [ "$lint" = true ]; then
    # lint
    ./scripts/lint.sh
fi

set -x

# run tests
pytest
