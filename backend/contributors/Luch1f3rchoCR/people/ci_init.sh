#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)/backend"

python - <<'PY'
import os, time, sys
import psycopg
host=os.getenv("POSTGRES_HOST","localhost")
port=int(os.getenv("POSTGRES_PORT","5432"))
user=os.getenv("POSTGRES_USER","postgres")
password=os.getenv("POSTGRES_PASSWORD","postgres")
dbname=os.getenv("POSTGRES_DB","postgres")
deadline=time.time()+120
while True:
    try:
        with psycopg.connect(host=host, port=port, user=user, password=password, dbname=dbname) as conn:
            break
    except Exception:
        if time.time()>deadline:
            sys.exit(1)
        print("waiting for postgres...")
        time.sleep(1)
PY

alembic -c backend/contributors/Luch1f3rchoCR/people/alembic.ini upgrade head
python -m backend.contributors.Luch1f3rchoCR.people.seeds
