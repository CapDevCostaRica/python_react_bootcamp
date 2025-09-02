$ErrorActionPreference = "Stop"

# Paths base
$ShipRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)   # .../contributors/capdevcr/shipments_lambdas
$CapRoot  = Split-Path -Parent $ShipRoot                                           # .../contributors/capdevcr
$BuildDir = Join-Path $CapRoot "infra\build"

$env:APP_SRC = "contributors/capdevcr/shipments_lambdas/app"

# Archivo de requirements a usar:
# - si tienes un requirements específico para estas lambdas, pon su ruta aquí
# - si no, suele estar en shipments_lambdas/requirements.txt
$env:REQ_FILE = "contributors/capdevcr/shipments_lambdas/requirements.txt"

# Limpiar build
if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Path $BuildDir | Out-Null

# Construir deps Linux-compatibles y empaquetar 2 funciones
docker run --rm `
  -v "$($CapRoot):/cap" `
  -w /cap `
  -e APP_SRC="$($env:APP_SRC)" `
  -e REQ_FILE="$($env:REQ_FILE)" `
  public.ecr.aws/sam/build-python3.11:latest `
  bash -lc @'
set -euo pipefail

# Variables desde -e
: "${APP_SRC:?APP_SRC is required}"
: "${REQ_FILE:?REQ_FILE is required}"

# Rutas absolutas dentro del contenedor
CAP="/cap"
BUILD="$CAP/contributors/capdevcr/infra/build"
APP_SRC_ABS="$CAP/$APP_SRC"
REQ_FILE_ABS="$CAP/$REQ_FILE"

# 1) site-packages para Lambda (Linux)
python -m pip install --upgrade pip
python -m pip install -r "$REQ_FILE_ABS" -t "$BUILD/_site"

# 2) Empaquetar funciones
python - << 'PY'
import os, shutil, zipfile, sys

CAP = "/cap"
BUILD = os.path.join(CAP, "contributors", "capdevcr", "infra", "build")
SITE = os.path.join(BUILD, "_site")
APP_SRC = os.path.join(CAP, os.environ["APP_SRC"])

functions = [
  ("login",         "app/functions/login/src/app.py"),
  ("list_shipments","app/functions/list_shipments/src/app.py"),
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
    outdir = os.path.join(BUILD, f"__{name}__")
    if os.path.exists(outdir): shutil.rmtree(outdir)
    shutil.copytree(SITE, outdir)                    # site-packages
    # Copiar toda la carpeta app/ (incluye auth.py, models.py, schemas.py y functions/*)
    shutil.copytree(APP_SRC, os.path.join(outdir, "app"), dirs_exist_ok=True)

    zpath = os.path.join(BUILD, f"{name}.zip")
    if os.path.exists(zpath): os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        zipdir(outdir, z)
    print(f"✅ {zpath}")
PY
'@

Write-Host "✅ Listo. Revisa: $BuildDir (login.zip, list_shipments.zip)"
