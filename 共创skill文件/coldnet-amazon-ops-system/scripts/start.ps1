$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = "C:\Users\ouyan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $python)) {
  $python = "python"
}

$env:HOST = "127.0.0.1"
$env:PORT = "8765"

Set-Location $projectRoot
& $python "backend\app.py"
