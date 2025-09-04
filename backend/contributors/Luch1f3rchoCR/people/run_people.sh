#!/usr/bin/env bash
set -euo pipefail
if [[ "${1-}" == "seed" ]]; then
  docker compose exec -T flask_app bash -lc \
    'PYTHONPATH=/app alembic -c /app/contributors/Luch1f3rchoCR/people/alembic.ini upgrade head && \
     PYTHONPATH=/app python -m contributors.Luch1f3rchoCR.people.seeds'
  exit 0
fi
docker compose logs -f flask_app