#!/usr/bin/env bash
set -euo pipefail
docker compose exec -T flask_db psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec -T flask_app bash -lc \
  'PYTHONPATH=/app alembic -c /app/contributors/Luch1f3rchoCR/people/alembic.ini upgrade head'
docker compose exec -T flask_app bash -lc \
  'PYTHONPATH=/app python -m contributors.Luch1f3rchoCR.people.seeds'
docker compose exec -T flask_db psql -U postgres -d postgres -Atc "SELECT count(*) FROM people;" \
  | awk '{print "Done. Seeded " $1 " people."}'