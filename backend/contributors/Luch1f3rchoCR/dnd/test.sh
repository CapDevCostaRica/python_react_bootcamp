#!/bin/bash
set -e

fail=0

echo "===> Smoke test: root"
resp=$(curl -s -w "%{http_code}" -o /tmp/root.json http://localhost:4000/)
code=${resp: -3}
if [ "$code" != "200" ]; then
  echo "root endpoint failed (HTTP $code)"
  fail=1
else
  cat /tmp/root.json | python3 -m json.tool
  echo "ok"
fi

echo "===> Smoke test: list monsters"
resp=$(curl -s -w "%{http_code}" -o /tmp/list.json \
  -X POST http://localhost:4000/handler \
  -H 'Content-Type: application/json' \
  -d '{"resource":"monsters"}')
code=${resp: -3}
if [ "$code" != "200" ]; then
  echo "list monsters failed (HTTP $code)"
  fail=1
else
  cat /tmp/list.json | python3 -m json.tool
  echo "monsters list ok"
fi

echo "===> Smoke test: get monster by slug (orc)"
resp=$(curl -s -w "%{http_code}" -o /tmp/orc.json \
  -X POST http://localhost:4000/handler \
  -H 'Content-Type: application/json' \
  -d '{"monster_index":"orc"}')
code=${resp: -3}
if [ "$code" != "200" ]; then
  echo "monster 'orc' failed (HTTP $code)"
  fail=1
else
  cat /tmp/orc.json | python3 -m json.tool
  echo "orc ok"
fi

exit $fail