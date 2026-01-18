#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
TEST_DIR='tests'

# Change directory to project root
cd "$PROJECT_ROOT" || exit 1

python -m unittest discover --start-directory "$TEST_DIR"
