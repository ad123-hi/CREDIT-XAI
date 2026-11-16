$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot 'backend'
$frontendDir = Join-Path $projectRoot 'frontend'

function Test-HttpEndpoint {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

if (-not (Test-Path (Join-Path $frontendDir 'dist'))) {
    Write-Host 'Building frontend...'
    Push-Location $frontendDir
    npm run build | Out-Host
    Pop-Location
}

if (-not (Test-HttpEndpoint 'http://127.0.0.1:8000')) {
    Write-Host 'Starting FastAPI backend...'
    Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'python', 'app.py' -WorkingDirectory $backendDir -WindowStyle Normal | Out-Null
}
else {
    Write-Host 'FastAPI backend is already running.'
}

if (-not (Test-HttpEndpoint 'http://127.0.0.1:3000')) {
    Write-Host 'Starting frontend server...'
    Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'npx', 'serve', '-s', 'dist', '-l', '3000' -WorkingDirectory $frontendDir -WindowStyle Normal | Out-Null
}
else {
    Write-Host 'Frontend server is already running.'
}

Write-Host ''
Write-Host '==========================================================='
Write-Host ' FastAPI backend  -> http://127.0.0.1:8000'
Write-Host ' Frontend UI      -> http://localhost:3000'
Write-Host '==========================================================='
