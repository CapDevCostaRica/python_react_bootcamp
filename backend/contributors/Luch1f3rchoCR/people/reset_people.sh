#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)/backend"

echo ">> Dropping & recreating schema (container DB)..."
docker exec -i python_react_bootcamp-flask_db-1 \
  psql -U postgres -d postgres -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo ">> Alembic upgrade head..."
alembic -c backend/contributors/Luch1f3rchoCR/people/alembic.ini upgrade head

echo ">> Seeding..."
python -m backend.contributors.Luch1f3rchoCR.people.seeds

echo ">> Verifying people count..."
docker exec -i python_react_bootcamp-flask_db-1 \
  psql -U postgres -d postgres -t -A -c "SELECT count(*) FROM people;" | \
  awk '{print ">> Done. Seeded " $1 " people."}'