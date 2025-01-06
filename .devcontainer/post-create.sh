#!/usr/bin/env bash

scripts/bootstrap

if ! pg_dump --schema-only --table=procrastinate_jobs 1>/dev/null 2>&1; then
    echo "Applying migrations"
    procrastinate schema --apply || return
fi

echo "Migrations applied!"

echo ""
echo "Welcome to the Procrastinate development container!"
echo ""
echo "You'll find the detailed instructions in the contributing documentation:"
echo "    https://procrastinate.readthedocs.io/en/latest/contributing.html"
echo ""
echo "TL;DR: important commands:"
echo "- pytest: Launch the tests"
echo "- tox: Entrypoint for testing multiple python versions as well as docs, linters & formatters"
echo "- procrastinate: Test procrastinate locally."
echo ""
echo "We've gone ahead and set up a few additional commands for you:"
echo "- htmlcov: Opens the test coverage results in your browser"
echo "- htmldoc: Opens the locally built sphinx documentation in your browser"
echo "- lint: Run code formatters & linters"
echo "- docs: Build doc"
