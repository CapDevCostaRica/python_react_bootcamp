#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "$0")" && pwd -P)"


if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd -P)"
fi

export PYTHONPATH="$REPO_ROOT/backend"

export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_DB="${POSTGRES_DB:-postgres}"
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"

export FLASK_APP="backend.contributors.Luch1f3rchoCR.people.main:app"
PORT="${FLASK_RUN_PORT:-5001}"


if [[ "${1-}" == "seed" ]]; then
  alembic -c "$REPO_ROOT/backend/contributors/Luch1f3rchoCR/people/alembic.ini" upgrade head
  python -m backend.contributors.Luch1f3rchoCR.people.seeds
fi

python -m flask --app "$FLASK_APP" run --host 0.0.0.0 --port "$PORT"