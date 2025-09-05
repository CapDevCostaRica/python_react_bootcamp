$ErrorActionPreference = "Stop"

$ShipRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CapRoot  = Split-Path -Parent $ShipRoot
$BuildDir = Join-Path $CapRoot "shipments_lambda\build"

$env:APP_SRC = "shipments_lambda/app"
$env:REQ_FILE = "shipments_lambda/requirements.txt"

if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Path $BuildDir | Out-Null

docker run --rm `
  -v "$($CapRoot):/cap" `
  -w /cap `
  -e APP_SRC="$($env:APP_SRC)" `
  -e REQ_FILE="$($env:REQ_FILE)" `
  public.ecr.aws/sam/build-python3.11:latest `
  bash -lc shipments_lambda/deploy/zip.sh

Write-Host "> Listo. Revisa: $BuildDir (login.zip, list_shipments.zip, update_shipment.zip, create_shipment.zip)"