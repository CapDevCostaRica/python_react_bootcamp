#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import os, time, psycopg
host=os.environ.get("POSTGRES_HOST","flask_db")
user=os.environ.get("POSTGRES_USER","postgres")
pwd =os.environ.get("POSTGRES_PASSWORD","postgres")
db  =os.environ.get("POSTGRES_DB","postgres")
port=os.environ.get("POSTGRES_PORT","5432")
for _ in range(60):
    try:
        psycopg.connect(host=host, user=user, password=pwd, dbname=db, port=port, connect_timeout=2).close()
        print("postgres ready"); break
    except Exception:
        print("waiting for postgres...", flush=True); time.sleep(1)
else:
    raise SystemExit("postgres not ready")
PY

if [[ "${ENABLE_FRAMEWORK_BOOTSTRAP:-0}" == "1" ]]; then
  python /app/framework/scripts/populate_database.py || true
fi

FLASK_APP_DEFAULT="contributors.Luch1f3rchoCR.people.main:app"
export FLASK_APP="${FLASK_APP:-$FLASK_APP_DEFAULT}"

flask run --host=0.0.0.0 --port=4000