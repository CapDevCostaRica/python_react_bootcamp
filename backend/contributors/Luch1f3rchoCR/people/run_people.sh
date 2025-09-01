#!/bin/bash
# Script to run the People API (ex02)

# Go to repo root
cd "$(dirname "$0")"

# Environment variables
export PYTHONPATH="$(pwd)/backend"
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=postgres
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export FLASK_APP=backend.contributors.Luch1f3rchoCR.people.main:app
export FLASK_RUN_PORT=5001

# Run Flask
python -m flask run
