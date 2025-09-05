#!/usr/bin/env bash

set -euo pipefail
: "${APP_SRC:?APP_SRC is required}"
: "${REQ_FILE:?REQ_FILE is required}"

CAP="/cap"
BUILD="$CAP/shipments_lambda/build"
APP_SRC_ABS="$CAP/$APP_SRC"
REQ_FILE_ABS="$CAP/$REQ_FILE"
python -m pip install --upgrade pip
python -m pip install -r "$REQ_FILE_ABS" -t "$BUILD/_site"
python - << 'PY'
import os, shutil, zipfile, sys
CAP = "/cap"
BUILD = os.path.join(CAP, "shipments_lambda", "build")
SITE = os.path.join(BUILD, "_site")
APP_SRC = os.path.join(CAP, os.environ["APP_SRC"])
functions = [
  ("login",         "functions/login/src/app.py"),
  ("list_shipments","functions/list_shipments/src/app.py"),
  ("create_shipment","functions/create_shipment/src/app.py"),
  ("update_shipment","functions/update_shipment/src/app.py"),
]
if not os.path.isdir(APP_SRC):
    print(f"[ERROR] APP_SRC no existe: {APP_SRC}", file=sys.stderr); sys.exit(1)
for name, rel_handler in functions:
    p = os.path.join(APP_SRC, rel_handler)
    if not os.path.isfile(p):
        print(f"[ERROR] No encuentro handler para {name}: {p}", file=sys.stderr); sys.exit(1)
def zipdir(root, zf):
    for r, _, files in os.walk(root):
        for f in files:
            p = os.path.join(r, f)
            zf.write(p, os.path.relpath(p, root))
for name, _ in functions:
    print("Zipping...")
    outdir = os.path.join(BUILD, f"__{name}__")
    if os.path.exists(outdir): shutil.rmtree(outdir)

    
    print(SITE, outdir)
    shutil.copytree(SITE, outdir)                    # site-packages


    # Copiar toda la carpeta app/ (incluye auth.py, models.py, schemas.py y functions/*)
    shutil.copytree(APP_SRC, os.path.join(outdir, "app"), dirs_exist_ok=True)
    zpath = os.path.join(BUILD, f"{name}.zip")

    print("zpath ")
    print(zpath)

    if os.path.exists(zpath): os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        zipdir(outdir, z)
    print(f"> {zpath}")
PY