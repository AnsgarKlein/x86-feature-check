#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

# Change directory to project root
cd "$PROJECT_ROOT" || exit 1

BINARY='x86-feature-check.py'

# Whether or not an error occurred
errors='no'


if ! command -v mypy > /dev/null 2> /dev/null; then
    echo 'Error: Can not run mypy!' > /dev/stderr
    echo 'mypy is not installed!' > /dev/stderr
else
    echo 'Running mypy...'
    if ! mypy $BINARY; then
        errors='yes'
    fi
fi
echo ''
echo ''


if ! command -v pytype > /dev/null 2> /dev/null; then
    echo 'Error: Can not run pytype!' > /dev/stderr
    echo 'pytype is not installed!' > /dev/stderr
else
    echo 'Running pytype...'
    if ! pytype $BINARY > /dev/null 2> /dev/null; then
        errors='yes'
    fi
fi
echo ''
echo ''


if ! command -v pylint > /dev/null 2> /dev/null; then
    echo 'Error: Can not run pylint!' > /dev/stderr
    echo 'pylint is not installed!' > /dev/stderr
else
    echo 'Running pylint...'
    pylint --exit-zero $BINARY
    if ! pylint --errors-only $BINARY > /dev/null 2> /dev/null; then
        errors='yes'
    fi
fi
echo ''
echo ''


# Return with error code if any linter returned an error
if [ "$errors" = 'yes' ]; then
    exit 1
fi

