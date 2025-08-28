#!/bin/bash
set -e

DB_SCRIPT=$1

if [ "$DB_SCRIPT" = "reset_db" ]; then
  python /app/framework/scripts/reset_db.py
  exit 0
elif [ "$DB_SCRIPT" = "populate_database" ]; then
  python /app/framework/scripts/populate_database.py
fi

flask run --host=0.0.0.0 --port=4000 --reload
