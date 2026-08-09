#!/usr/bin/env pwsh
# Starts Django dev server and the background task worker together.

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $repo ".rag~\Scripts\python.exe"
$manage = Join-Path $repo "manage.py"

function Start-Process-Log {
    param(
        [string]$Name,
        [string]$FilePath,
        [string]$ArgumentList
    )
    Write-Host "Starting $Name..."
    Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -PassThru
}

Write-Host "Starting RAG Knowledge Assistant development environment..."

$existing = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*$manage*" -or $_.CommandLine -like '*summarizer\.rag~*db_worker*'
}
if ($existing) {
    Write-Host "Already running:"
    $existing | ForEach-Object { Write-Host "  PID $($_.ProcessId): $($_.CommandLine)" }
    Write-Host "Stop the existing processes before starting a new one to avoid port conflicts and orphan workers."
    exit 1
}

$worker = Start-Process-Log -Name "Django background worker" -FilePath $python -ArgumentList "$manage db_worker"
Start-Sleep -Seconds 2
$server = Start-Process-Log -Name "Django development server" -FilePath $python -ArgumentList "$manage runserver 0.0.0.0:8000 --noreload"

Write-Host "Backend services started. Worker PID: $($worker.Id), Server PID: $($server.Id)"
Write-Host "Press Ctrl+C in this terminal to stop all Python processes when done."

# Keep the script alive so the terminal doesn't return to the prompt immediately.
try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($worker.HasExited -and $server.HasExited) {
            break
        }
    }
} finally {
    if (-not $worker.HasExited) { Stop-Process -Id $worker.Id -Force }
    if (-not $server.HasExited) { Stop-Process -Id $server.Id -Force }
}
