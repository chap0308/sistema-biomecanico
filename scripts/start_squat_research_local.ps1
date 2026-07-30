param(
    [string]$PythonPath = "D:\anaconda4\envs\analisis-bio\python.exe",
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000
)

$ErrorActionPreference = "Stop"
$workspace = Split-Path -Parent $PSScriptRoot
$logDirectory = Join-Path $workspace "output\playwright"
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

$supabaseEnvironment = @{}
$strictErrorPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$supabaseStatus = & (Get-Command supabase.cmd).Source status -o env 2>$null
$ErrorActionPreference = $strictErrorPreference
$supabaseStatus | ForEach-Object {
    if ($_ -match '^([A-Z0-9_]+)="?(.*?)"?$') {
        $supabaseEnvironment[$matches[1]] = $matches[2].Trim('"')
    }
}

if (-not $supabaseEnvironment["API_URL"]) {
    throw "Supabase local no está activo. Ejecuta 'supabase start' primero."
}

$env:SUPABASE_URL = $supabaseEnvironment["API_URL"]
$env:SUPABASE_PUBLISHABLE_KEY = $supabaseEnvironment["PUBLISHABLE_KEY"]
$env:SUPABASE_SECRET_KEY = $supabaseEnvironment["SECRET_KEY"]
$env:SUPABASE_ANON_KEY = $supabaseEnvironment["ANON_KEY"]
$env:SUPABASE_SERVICE_KEY = $supabaseEnvironment["SERVICE_ROLE_KEY"]
$env:SQUAT_AUTH_REQUIRED = "true"
$env:SQUAT_PERSISTENCE_REQUIRED = "true"

$occupiedPorts = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in @($ApiPort, $WebPort) }
if ($occupiedPorts) {
    $ports = ($occupiedPorts.LocalPort | Sort-Object -Unique) -join ", "
    throw "Los puertos $ports ya están ocupados. Detén esos procesos antes de iniciar."
}

$api = Start-Process `
    -FilePath $PythonPath `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $ApiPort `
    -WorkingDirectory $workspace `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $logDirectory "api-$ApiPort.out.log") `
    -RedirectStandardError (Join-Path $logDirectory "api-$ApiPort.err.log") `
    -PassThru

$npm = (Get-Command npm.cmd).Source
$web = Start-Process `
    -FilePath $npm `
    -ArgumentList "start", "--", "-H", "0.0.0.0", "-p", $WebPort `
    -WorkingDirectory (Join-Path $workspace "apps\web") `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $logDirectory "web-$WebPort.out.log") `
    -RedirectStandardError (Join-Path $logDirectory "web-$WebPort.err.log") `
    -PassThru

Write-Output "FastAPI: http://127.0.0.1:$ApiPort (PID $($api.Id))"
Write-Output "Next.js: http://127.0.0.1:$WebPort (PID $($web.Id))"
Write-Output "Autenticación y persistencia de sentadilla: activadas"
