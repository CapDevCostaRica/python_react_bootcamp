#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# test.sh - Run the same steps as the CI docker-ci workflow locally.
# Usage: ./test.sh [--application-folder|-a <user/project>] [--test-folder|-t <tests/path>]
# Example: ./test.sh -a capdevcr/boilerplate -t tests/exercises/session_2
# Requirements: docker (with compose v2), git, pytest installed locally (or in a virtualenv)

usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  -a, --application-folder  APPLICATION_FOLDER to test (format user/project). If provided, git detection is skipped.
  -t, --test-folder         TEST_FOLDER path for pytest (overrides test.env/.env)
  -h, --help                Show this help and exit

Example:
  APPLICATION_FOLDER=capdevcr/boilerplate TEST_FOLDER=tests/exercises/session_2 ./test.sh
  or
  ./test.sh -a capdevcr/boilerplate -t tests/exercises/session_2
EOF
}

# parse args
while [[ ${#@} -gt 0 ]]; do
  case "$1" in
    -a|--application-folder)
      APPLICATION_FOLDER="$2"
      shift 2
      ;;
    -t|--test-folder)
      TEST_FOLDER="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

cleanup() {
  echo "Tearing down docker-compose services..."
  docker compose down -v || true
}
trap cleanup EXIT

# If APPLICATION_FOLDER provided via env/args use it, otherwise detect from git changes
if [ -n "${APPLICATION_FOLDER:-}" ]; then
  echo "APPLICATION_FOLDER provided: $APPLICATION_FOLDER"
else
  echo "Detecting changed contributor folder..."
  # Try to use origin/main...HEAD, fallback to HEAD~1..HEAD
  CHANGED=""
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    CHANGED=$(git diff --name-only origin/main...HEAD || true)
  fi
  if [ -z "$CHANGED" ]; then
    CHANGED=$(git diff --name-only HEAD~1..HEAD || true)
  fi

  if [ -z "$CHANGED" ]; then
    echo "No changed files detected via git. You must provide APPLICATION_FOLDER via -a/--application-folder or set APPLICATION_FOLDER env var."
    exit 1
  fi

  echo "Changed files:\n$CHANGED"

  APPS=$(echo "$CHANGED" | grep -Eo '^backend/contributors/[^/]+/[^/]+' || true | sort -u)
  if [ -z "$APPS" ]; then
    echo "ERROR: No changes under backend/contributors detected. Provide APPLICATION_FOLDER via env or args."
    exit 1
  fi

  APPS_COUNT=$(echo "$APPS" | wc -l)
  if [ "$APPS_COUNT" -gt 1 ]; then
    echo "ERROR: Multiple contributor app folders modified: \n$APPS"
    exit 1
  fi

  APP_FULL=$(echo "$APPS" | head -n1)
  APP_REL=${APP_FULL#backend/contributors/}
  # Ensure all changed files are inside this app folder
  if echo "$CHANGED" | grep -v -E "^backend/contributors/$APP_REL/" | grep -q .; then
    echo "ERROR: Found changed files outside detected app folder backend/contributors/$APP_REL"
    echo "Changed files outside the app:"
    echo "$CHANGED" | grep -v -E "^backend/contributors/$APP_REL/"
    exit 1
  fi
  APPLICATION_FOLDER="$APP_REL"
  export APPLICATION_FOLDER
  echo "Detected APPLICATION_FOLDER=$APPLICATION_FOLDER"
fi

CONTRIB_DIR="backend/contributors/$APPLICATION_FOLDER"
TEST_ENV_PATH="$CONTRIB_DIR/test.env"
if [ ! -f "$TEST_ENV_PATH" ]; then
  echo "ERROR: Required file $TEST_ENV_PATH not found. The contributor folder must include test.env"
  exit 1
fi

# Load test.env variables into environment (do not overwrite existing)
echo "Loading $TEST_ENV_PATH"
while IFS= read -r line; do
  # skip comments and blank lines
  [[ "$line" =~ ^\s*# ]] && continue
  [[ -z "$line" ]] && continue
  key="${line%%=*}"
  val="${line#*=}"
  if [ -z "${!key:-}" ]; then
    export "$key=$val"
    echo "Key $key added"
  else
    echo "Key $key already set in environment; keeping existing value"
  fi
done < <(cat "$TEST_ENV_PATH")

# Load .env (optional) but do not overwrite keys already set
if [ -f .env ]; then
  echo "Loading .env (skipping keys already set)"
  while IFS= read -r line; do
    [[ "$line" =~ ^\s*# ]] && continue
    [[ -z "$line" ]] && continue
    key="${line%%=*}"
    val="${line#*=}"
    if [ "$key" = "APPLICATION_FOLDER" ]; then
      echo "Skipping APPLICATION_FOLDER from .env to preserve detected value"
      continue
    fi
    if [ -z "${!key:-}" ]; then
      export "$key=$val"
    fi
  done < <(cat .env)
fi

# Allow TEST_FOLDER override via CLI/ENV already parsed earlier
if [ -n "${TEST_FOLDER:-}" ]; then
  export TEST_FOLDER
fi

if [ -z "${TEST_FOLDER:-}" ]; then
  echo "ERROR: TEST_FOLDER is not set. Please set TEST_FOLDER in test.env or .env or export it before running this script." 
  exit 1
fi

# Prepare .env for docker-compose: copy .env.example if .env not present and set APPLICATION_FOLDER
if [ -f .env ]; then
  echo ".env already exists locally"
else
  if [ -f .env.example ]; then
    cp .env.example .env
  else
    echo "ERROR: .env.example not found in repo root"
    exit 1
  fi
fi
# Update APPLICATION_FOLDER in .env
if grep -q '^APPLICATION_FOLDER=' .env; then
  sed -i.bak "s|^APPLICATION_FOLDER=.*|APPLICATION_FOLDER=${APPLICATION_FOLDER}|" .env && rm -f .env.bak || true
else
  echo "APPLICATION_FOLDER=${APPLICATION_FOLDER}" >> .env
fi

echo ".env content:" 
cat .env

# Start docker-compose
echo "Starting docker compose (build & up)"
docker compose up -d --build

# Run reset_db inside flask_app
echo "Running reset_db inside flask_app container"
docker compose run --rm flask_app bash /app/run_local.sh reset_db

# Wait for Postgres
echo "Waiting for Postgres to be ready..."
for i in {1..30}; do
  if docker compose exec -T flask_db pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-postgres}; then
    echo "Postgres ready"
    break
  fi
  sleep 2
done

# Ensure pytest is available
if ! command -v pytest >/dev/null 2>&1; then
  echo "ERROR: pytest not found. Install pytest to run tests." >&2
  exit 1
fi

# Run pytest
TEST_PATH="${TEST_FOLDER#/}"
echo "Running pytest on: $TEST_PATH"
pytest -sq  "$TEST_PATH"

# cleanup will be run by trap
exit 0
