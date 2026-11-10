# Supervised OWNED Windows Sandbox normal-flow acceptance; original runtime only.
[CmdletBinding()]
param(
    [ValidateSet('Preflight','Run','Record','Show')][string]$Action = 'Preflight',
    [string]$StorageRoot,
    [string]$Session,
    [string]$Case,
    [ValidateSet('PASS','FAIL','BLOCKED')][string]$Result,
    [switch]$Setup,
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
    # Check run consent BEFORE setup/private configuration. No automatic effects.
    if ($Action -eq 'Run' -and -not ($Session -and $StorageRoot -and $SandboxOnly -and $EnableRealPrinter -and $AcceptRealPaper -and $EnableRealDrive -and $AcceptPublicTestUpload)) {
        throw 'Run requires the preflight session, SAME storage, explicit Sandbox and BOTH original consent pairs.'
    }
    if ($Action -in @('Preflight','Run') -and -not $StorageRoot) { throw 'Use the SAME original StorageRoot.' }
    if ($Action -in @('Run','Record','Show') -and -not $Session) { throw 'Use a recorded acceptance session.' }
    if ($Action -eq 'Record' -and -not ($Case -and $Result)) { throw 'Record requires Case and Result; no notes or proofs.' }
    if ($Setup -and $Action -ne 'Preflight') { throw 'Setup is dependency-only and requires Action Preflight.' }
    if ($Setup) {
        & "$PSScriptRoot\Start-PostPreviewDeviceTest.ps1" -Setup -CheckOnly
        if ($LASTEXITCODE -ne 0) { throw 'Original dependency setup held.' }
    }
    $meongAcceptancePython = $null
    foreach ($meongCandidate in @('.venv-kivy\Scripts\python.exe','.venv\Scripts\python.exe')) {
        if (Test-Path $meongCandidate) { $meongAcceptancePython = Join-Path $PSScriptRoot $meongCandidate; break }
    }
    if (-not $meongAcceptancePython) { throw 'Use Action Preflight -Setup with Python 3.12 installed.' }
    $meongAcceptanceArgs = @('tools/run_post_preview_acceptance.py')
    switch ($Action) {
        'Preflight' { $meongAcceptanceArgs += @('preflight','--storage-root',$StorageRoot,'--booth-id',$BoothId) }
        'Run' { $meongAcceptanceArgs += @('validate-run','--storage-root',$StorageRoot,'--booth-id',$BoothId,'--session',$Session) }
        'Record' { $meongAcceptanceArgs += @('record','--session',$Session,'--case',$Case,'--result',$Result) }
        'Show' { $meongAcceptanceArgs += @('show','--session',$Session) }
    }
    & $meongAcceptancePython @meongAcceptanceArgs
    $meongAcceptanceCode = $LASTEXITCODE
    if ($Action -eq 'Run' -and $meongAcceptanceCode -eq 0) {
        # SAME original launcher and explicit original consent flags; no new GUI.
        & "$PSScriptRoot\Start-PostPreviewSandbox.ps1" -StorageRoot $StorageRoot -BoothId $BoothId -Size $Size -CameraIndex $CameraIndex `
            -SandboxOnly -EnableRealPrinter -AcceptRealPaper -EnableRealDrive -AcceptPublicTestUpload
        $meongAcceptanceCode = $LASTEXITCODE
    }
} catch {
    # Do not echo dynamic OS errors, arguments, credentials, URLs or proof text.
    Write-Output 'BLOCKED: acceptance entry held. Preserve original history; check the documented flags and prerequisites.'
    $meongAcceptanceCode = 2
} finally { Pop-Location }
exit $meongAcceptanceCode
