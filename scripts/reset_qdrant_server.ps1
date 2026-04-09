param(
    [switch]$FullReset,
    [string[]]$Collections = @("video_segments_v1")
)

$ErrorActionPreference = "Stop"

$serverProcess = Get-Process -Name "qdrant" -ErrorAction SilentlyContinue
if ($serverProcess) {
    Write-Output "Stopping Qdrant PID=$($serverProcess.Id)"
    Stop-Process -Id $serverProcess.Id -Force
    Start-Sleep -Seconds 2
}

$storageRoot = "D:\sistema-biomecanico\data\qdrant_server\storage"
$collectionsRoot = Join-Path $storageRoot "collections"

if ($FullReset) {
    if (Test-Path $storageRoot) {
        Write-Output "Removing full Qdrant server storage: $storageRoot"
        Remove-Item -LiteralPath $storageRoot -Recurse -Force
    }
}
else {
    foreach ($collectionName in $Collections) {
        $collectionPath = Join-Path $collectionsRoot $collectionName
        if (Test-Path $collectionPath) {
            Write-Output "Removing collection directory: $collectionPath"
            Remove-Item -LiteralPath $collectionPath -Recurse -Force
        }
    }
}

& powershell -ExecutionPolicy Bypass -File "D:\sistema-biomecanico\scripts\start_qdrant_server.ps1"
