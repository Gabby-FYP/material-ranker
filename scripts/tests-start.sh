#! /usr/bin/env bash
set -e
set -x

python src/scripts/tests_pre_start.py

bash scripts/test.sh "$@"
