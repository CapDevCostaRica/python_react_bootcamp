#!/usr/bin/env bash
set -e


until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "waiting for postgres..."; sleep 1
done


if [ "${RUN_FRAMEWORK:-0}" = "1" ]; then
  echo "[run_local] Running framework populate (RUN_FRAMEWORK=1)"
  python /app/framework/scripts/populate_database.py
else
  echo "[run_local] Skipping framework populate (RUN_FRAMEWORK!=1)"
fi


flask --app app.main run --host=0.0.0.0 --port=4000