$ErrorActionPreference = "Stop"

$ShipRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)   # .../contributors/name/shipments_lambdas
$CapRoot  = Split-Path -Parent $ShipRoot                                           # .../contributors/name
$BuildDir = Join-Path $CapRoot "infra\build"

$env:APP_SRC = "shipments_lambdas/app"
$env:REQ_FILE = "shipments_lambdas/requirements.txt"

if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Path $BuildDir | Out-Null

Write-Host "1. PATHS: $env:APP_SRC "
Write-Host "2. PATHS: $env:REQ_FILE "
Write-Host "3. PATHS: $CapRoot "

docker run --rm `
  -v "$($CapRoot):/cap" `
  -w /cap `
  -e APP_SRC="$($env:APP_SRC)" `
  -e REQ_FILE="$($env:REQ_FILE)" `
  public.ecr.aws/sam/build-python3.11:latest `
  bash /cap/shipments_lambdas/build_lambda.sh

Write-Host "✅ Listo. Revisa: $BuildDir (login.zip, list_shipments.zip)"
