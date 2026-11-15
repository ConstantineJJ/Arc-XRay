param([switch]$DryRun, [switch]$CheckOnly)
# Windows PowerShell 5.1 compatible; also works when downloaded with irm | iex.
# Do not change PATH, execution policy, or other plugin configuration.
$arcPreviousErrorPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Stop'
    if ($DryRun) {
        Write-Output 'codex plugin marketplace add ConstantineJJ/Arc-XRay'
        Write-Output 'codex plugin marketplace upgrade arc-xray'
        Write-Output 'codex plugin add arc-xray@arc-xray'
        return
    }
    $arcCommand = Get-Command codex.exe -ErrorAction SilentlyContinue
    if (-not $arcCommand) { $arcCommand = Get-Command codex -ErrorAction SilentlyContinue }
    $arcExecutable = if ($arcCommand) { $arcCommand.Source } else { $null }
    if (-not $arcExecutable -and (Get-Command Get-AppxPackage -ErrorAction SilentlyContinue)) {
        $arcDesktop = Get-AppxPackage -Name OpenAI.Codex -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($arcDesktop) {
            $arcCandidate = Join-Path $arcDesktop.InstallLocation 'app\resources\codex.exe'
            if (Test-Path -LiteralPath $arcCandidate -PathType Leaf) { $arcExecutable = $arcCandidate }
        }
    }
    if (-not $arcExecutable) {
        throw 'Codex not found. Install the Codex desktop app or a CLI with plugin support, then run this installer again. Administrator rights are not required.'
    }
    & $arcExecutable plugin marketplace add --help | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Update Codex: this CLI does not support plugin marketplaces.' }
    & $arcExecutable plugin add --help | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Update Codex: this CLI does not support plugin installation.' }
    & $arcExecutable plugin marketplace upgrade --help | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Update Codex: this CLI does not support marketplace refresh.' }
    if ($CheckOnly) {
        & $arcExecutable --version
        Write-Output 'PASS: Codex found and plugin commands available. Nothing installed.'
        return
    }
    & $arcExecutable plugin marketplace add ConstantineJJ/Arc-XRay
    if ($LASTEXITCODE -ne 0) { throw 'Marketplace registration failed; installation stopped.' }
    & $arcExecutable plugin marketplace upgrade arc-xray
    if ($LASTEXITCODE -ne 0) { throw 'Arc-XRay marketplace refresh failed; installation stopped.' }
    & $arcExecutable plugin add arc-xray@arc-xray
    if ($LASTEXITCODE -ne 0) { throw 'Plugin installation failed.' }
    Write-Output 'Arc-XRay installed. Open a new chat and select Arc-XRay. No MCP server required.'
} finally {
    $ErrorActionPreference = $arcPreviousErrorPreference
}
