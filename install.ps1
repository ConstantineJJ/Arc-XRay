param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
if ($DryRun) {
    Write-Output 'codex plugin marketplace add ConstantineJJ/Arc-XRay'
    Write-Output 'codex plugin add arc-xray@arc-xray'
    exit 0
}
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw 'Install/update Codex CLI, or use Plugins > Upload plugin archive in the app.' }
codex plugin marketplace add ConstantineJJ/Arc-XRay
if ($LASTEXITCODE -ne 0) { throw 'Marketplace registration failed; installation stopped.' }
codex plugin add arc-xray@arc-xray
if ($LASTEXITCODE -ne 0) { throw 'Plugin installation failed.' }
Write-Output 'Arc-XRay installed. Open a new chat and select Arc-XRay. No MCP server required.'
