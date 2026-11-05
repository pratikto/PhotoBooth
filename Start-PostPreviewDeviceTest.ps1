# Dedicated synthetic-payment physical trial; no branch switch or device defaults elsewhere.
[CmdletBinding()]
param(
    [switch]$Setup,
    [switch]$CheckOnly,
    [ValidateSet('452x900', '800x1280')][string]$Size = '452x900',
    [ValidateRange(0, 32)][int]$CameraIndex = 0,
    [switch]$EnableRealPrinter,
    [switch]$AcceptRealPaper,
    [switch]$EnableRealDrive,
    [switch]$AcceptPublicTestUpload
)
$ErrorActionPreference = 'Stop'
$meongRoot = $PSScriptRoot
Push-Location $meongRoot
try {
    $meongBranch = & git branch --show-current
    if ($LASTEXITCODE -ne 0 -or "$meongBranch".Trim() -ne 'feature/post-preview-qris-checkout') {
        throw 'Use the existing feature/post-preview-qris-checkout checkout. No branch was changed.'
    }
    $meongPython = $null
    foreach ($meongCandidate in @('.venv-kivy\Scripts\python.exe', '.venv\Scripts\python.exe')) {
        if (Test-Path $meongCandidate) {
            $meongPython = Join-Path $meongRoot $meongCandidate
            break
        }
    }
    if (-not $meongPython) {
        if (-not $Setup) { throw 'No existing venv found. Run this script once with -Setup -CheckOnly.' }
        if (Test-Path '.venv-kivy') { throw 'Existing .venv-kivy has no usable Python. Preserve it and repair the environment first.' }
        $meongPathPython = $false
        if (Get-Command python -ErrorAction SilentlyContinue) {
            $meongVersion = & python -c "import sys; print(str(sys.version_info[0])+'.'+str(sys.version_info[1]))"
            $meongPathPython = ($LASTEXITCODE -eq 0 -and "$meongVersion".Trim() -eq '3.12')
        }
        if ($meongPathPython) {
            & python -m venv .venv-kivy
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3.12 -m venv .venv-kivy
        } else { throw 'Install Python 3.12 with its launcher, then rerun -Setup -CheckOnly.' }
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed; no device was opened.' }
        $meongPython = Join-Path $meongRoot '.venv-kivy\Scripts\python.exe'
    }
    if ($Setup) {
        & $meongPython -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Resolve it before opening devices.' }
        & $meongPython -m pip check
        if ($LASTEXITCODE -ne 0) { throw 'Dependency conflicts found; no device was opened.' }
    }
    $meongArgs = @('tools/start_post_preview_device_test.py', '--size', $Size, '--camera-index', "$CameraIndex")
    if ($CheckOnly) { $meongArgs += '--check-only' }
    if ($EnableRealPrinter) { $meongArgs += '--enable-real-printer' }
    if ($AcceptRealPaper) { $meongArgs += '--accept-real-paper' }
    if ($EnableRealDrive) { $meongArgs += '--enable-real-drive' }
    if ($AcceptPublicTestUpload) { $meongArgs += '--accept-public-test-upload' }
    & $meongPython @meongArgs
    $meongCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $meongCode
