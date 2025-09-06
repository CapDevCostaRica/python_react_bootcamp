$ErrorActionPreference = "Stop"

$ShipRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)   # .../contributors/name/shipments_lambdas
$CapRoot  = Split-Path -Parent $ShipRoot                                           # .../contributors/name
$BuildDir = Join-Path $CapRoot "infra\build"

$env:APP_SRC = "contributors/capdevcr/shipments_lambdas/app"
$env:REQ_FILE = "contributors/capdevcr/shipments_lambdas/requirements.txt"

if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Path $BuildDir | Out-Null

docker run --rm `
  -v "$($CapRoot):/cap" `
  -w /cap `
  -e APP_SRC="$($env:APP_SRC)" `
  -e REQ_FILE="$($env:REQ_FILE)" `
  public.ecr.aws/sam/build-python3.11:latest `
  bash /cap/contributors/capdevcr/build_lambda.sh


Write-Host "✅ Listo. Revisa: $BuildDir (login.zip, list_shipments.zip)"
