# Fail fast + verbose visibility
$ErrorActionPreference = "Stop"

# Configuration
$PythonVersions = @("3.13", "3.12", "3.11", "3")
$VenvName = ".venv"
$VenvMarker = "pyvenv.cfg"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-VirtualEnvActive {
    return [bool]$env:VIRTUAL_ENV
}

function Get-VirtualEnvPath {
    param([string]$ServiceRoot)
    return Join-Path $ServiceRoot $VenvName
}

function Test-VirtualEnvExists {
    param([string]$ServiceRoot)
    $venvPath = Get-VirtualEnvPath -ServiceRoot $ServiceRoot
    $markerPath = Join-Path $venvPath $VenvMarker
    return Test-Path $markerPath
}

function New-VirtualEnv {
    param([string]$ServiceRoot)
    $venvPath = Get-VirtualEnvPath -ServiceRoot $ServiceRoot
    
    Write-Info "Creating virtualenv at $venvPath"
    
    foreach ($version in $PythonVersions) {
        try {
            & py "-$version" -m venv $venvPath 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Info "Virtualenv created successfully with Python $version"
                return $true
            }
        }
        catch {
            Write-Warning "Failed to create virtualenv with Python $version"
        }
    }
    
    throw "Failed to create virtualenv with any Python version"
}

function Activate-VirtualEnv {
    param([string]$ServiceRoot)
    $venvPath = Get-VirtualEnvPath -ServiceRoot $ServiceRoot
    $activatePs1 = Join-Path $venvPath "Scripts\Activate.ps1"
    $activateBat = Join-Path $venvPath "Scripts\activate.bat"
    
    if (Test-Path $activatePs1) {
        Write-Info "Activating venv via PowerShell: $activatePs1"
        . "$activatePs1"
        return $true
    }
    elseif (Test-Path $activateBat) {
        Write-Warning "PS1 activator not found. Using BAT fallback: $activateBat"
        cmd /c "$activateBat `& echo VENV_ACTIVATED `& powershell -NoExit"
        throw "Please re-run install.ps1 in the activated PowerShell session."
    }
    else {
        throw "Virtualenv activation script not found. Check that .venv was created and contains Scripts\Activate.ps1."
    }
}

function Install-Dependencies {
    param([string]$ServiceRoot)
    
    Write-Info "Installing baseline toolchain..."
    python -m pip install --upgrade pip wheel setuptools
    
    Write-Info "Installing global baseline requirements..."
    $globalRequirements = Join-Path $ServiceRoot "..\..\..\requirements.txt"
    Write-Info "Looking for global requirements at: $globalRequirements"
    if (Test-Path $globalRequirements) {
        Write-Info "Found global requirements, installing..."
        pip install -r $globalRequirements
    } else {
        Write-Warning "Global requirements.txt not found at: $globalRequirements"
    }
    
    Write-Info "Installing service requirements..."
    $serviceRequirements = Join-Path $ServiceRoot "requirements.txt"
    if (Test-Path $serviceRequirements) {
        pip install -r $serviceRequirements
    } else {
        Write-Warning "Service requirements.txt not found at: $serviceRequirements"
    }
}

# Main execution
function Main {
    # Compute service root (…\dnd) from scripts/
    $ServiceRoot = Split-Path -Parent $PSScriptRoot
    Set-Location $ServiceRoot
    Write-Info "ServiceRoot = $ServiceRoot"
    
    # Check if virtualenv is already active
    if (Test-VirtualEnvActive) {
        Write-Info "Virtualenv already active: $env:VIRTUAL_ENV"
    } else {
        # Create virtualenv if it doesn't exist
        if (-not (Test-VirtualEnvExists -ServiceRoot $ServiceRoot)) {
            New-VirtualEnv -ServiceRoot $ServiceRoot
        }
        
        # Activate virtualenv
        Activate-VirtualEnv -ServiceRoot $ServiceRoot
    }
    
    # Install dependencies
    Install-Dependencies -ServiceRoot $ServiceRoot
    
    Write-Success "Dependencies installed for danielmadriz/dnd"
}

# Run main function
try {
    Main
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
