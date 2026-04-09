param(
    [string]$ConfigPath = "D:\sistema-biomecanico\tools\qdrant-server\config\config.yaml"
)

$ErrorActionPreference = "Stop"

$serverDir = "D:\sistema-biomecanico\tools\qdrant-server"
$binaryPath = Join-Path $serverDir "qdrant.exe"

if (-not (Test-Path $binaryPath)) {
    throw "Qdrant binary not found at $binaryPath"
}

$configDir = Split-Path -Parent $ConfigPath
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
New-Item -ItemType Directory -Force -Path "D:\sistema-biomecanico\data\qdrant_server\storage" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\sistema-biomecanico\data\qdrant_server\snapshots" | Out-Null

if (-not (Test-Path $ConfigPath)) {
@"
log_level: INFO
storage:
  storage_path: D:/sistema-biomecanico/data/qdrant_server/storage
  snapshots_path: D:/sistema-biomecanico/data/qdrant_server/snapshots
service:
  host: 127.0.0.1
  http_port: 6333
  grpc_port: 6334
"@ | Set-Content -Path $ConfigPath -Encoding UTF8
}

$existing = Get-Process -Name "qdrant" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Output "Qdrant already running. PID=$($existing[0].Id)"
    exit 0
}

$proc = Start-Process -FilePath $binaryPath -ArgumentList "--config-path", $ConfigPath, "--disable-telemetry" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:6333/collections" -UseBasicParsing
    Write-Output "Qdrant started. PID=$($proc.Id)"
    Write-Output "Collections endpoint: http://127.0.0.1:6333/collections"
    Write-Output $response.Content
}
catch {
    throw "Qdrant process started with PID $($proc.Id), but the HTTP endpoint did not respond correctly."
}
