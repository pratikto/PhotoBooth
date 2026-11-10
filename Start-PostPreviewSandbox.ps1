# Explicit protected Sandbox entry. Original synthetic device helper is unchanged.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$StorageRoot,
    [switch]$Setup,
    [switch]$CheckOnly,
    [switch]$SetupOnly,
    [switch]$EnrollNewBooth,
    [switch]$SandboxOnly,
    [string]$BoothId = 'PB001',
    [ValidateSet('452x900','800x1280')][string]$Size = '452x900',
    [ValidateRange(0,32)][int]$CameraIndex = 0,
    [switch]$EnableRealPrinter,
    [switch]$AcceptRealPaper,
    [switch]$EnableRealDrive,
    [switch]$AcceptPublicTestUpload
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $meongBranch = & git branch --show-current
    if ($LASTEXITCODE -ne 0 -or "$meongBranch".Trim() -ne 'feature/post-preview-qris-checkout') {
        throw 'Use the existing feature/post-preview-qris-checkout. No branch was changed.'
    }
    $meongLocalSetup = $SetupOnly -or $EnrollNewBooth
    if ($meongLocalSetup -and (-not ($SetupOnly -and $EnrollNewBooth -and $SandboxOnly) -or $CheckOnly -or $EnableRealPrinter -or $AcceptRealPaper -or $EnableRealDrive -or $AcceptPublicTestUpload)) {
        throw 'Local setup requires -SetupOnly -EnrollNewBooth -SandboxOnly, without run/check flags.'
    }
    if (-not $CheckOnly -and -not $meongLocalSetup -and -not ($SandboxOnly -and $EnableRealPrinter -and $AcceptRealPaper -and $EnableRealDrive -and $AcceptPublicTestUpload)) {
        throw 'Explicit Sandbox and both original paper/Drive consent pairs are required.'
    }
    if ($Setup) {
        # Reuse dependency setup only; never launch its synthetic GUI here.
        & "$PSScriptRoot\Start-PostPreviewDeviceTest.ps1" -Setup -CheckOnly
        if ($LASTEXITCODE -ne 0) { throw 'Dependency preflight failed; no protected backend/device was opened.' }
    }
    $meongPython = $null
    foreach ($meongCandidate in @('.venv-kivy\Scripts\python.exe','.venv\Scripts\python.exe')) {
        if (Test-Path $meongCandidate) { $meongPython = Join-Path $PSScriptRoot $meongCandidate; break }
    }
    if (-not $meongPython) { throw 'Run once with -Setup -CheckOnly using Python 3.12.' }
    $meongArgs = @('tools/run_post_preview_sandbox.py','--storage-root',$StorageRoot,'--booth-id',$BoothId,'--size',$Size,'--camera-index',"$CameraIndex")
    if ($CheckOnly) { $meongArgs += '--check-only' }
    if ($SetupOnly) { $meongArgs += '--setup-only' }
    if ($EnrollNewBooth) { $meongArgs += '--enroll-new-booth' }
    if ($SandboxOnly) { $meongArgs += '--sandbox-only' }
    if ($EnableRealPrinter) { $meongArgs += '--enable-real-printer' }
    if ($AcceptRealPaper) { $meongArgs += '--accept-real-paper' }
    if ($EnableRealDrive) { $meongArgs += '--enable-real-drive' }
    if ($AcceptPublicTestUpload) { $meongArgs += '--accept-public-test-upload' }
    & $meongPython @meongArgs
    $meongCode = $LASTEXITCODE
} finally { Pop-Location }
exit $meongCode
