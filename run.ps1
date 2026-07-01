$venv = Join-Path $PSScriptRoot 'venv'
$activateScript = Join-Path $venv 'Scripts\Activate.ps1'
if (-not (Test-Path $activateScript)) {
    Write-Error 'Virtual environment not found. Run: python -m venv venv'
    exit 1
}
& $activateScript
python main.py $args
