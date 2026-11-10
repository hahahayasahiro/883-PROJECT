$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) { python -m venv .venv }
if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (-not (Test-Path '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
& '.\.venv\Scripts\python.exe' manage.py
if ($LASTEXITCODE -ne 0) { throw 'Database initialization or migration failed.' }
Write-Host 'Ready. Edit .env to configure DeepSeek, then run start.cmd.'
