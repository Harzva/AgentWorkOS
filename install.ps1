[CmdletBinding()]
param(
    [ValidateSet("base", "codex", "just-ddl", "full")]
    [string]$Profile = "codex",
    [ValidateSet("codex", "claude-code", "claude", "all")]
    [string]$Target = "codex",
    [switch]$Apply,
    [string]$AwHome = ""
)

$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Warning "PowerShell 7+ is recommended for UTF-8 paths and cross-platform behavior."
}

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
try {
    python -m pip install -e .

    $manifest = Join-Path $root "agentworkos.toml"
    python -m agentworkos.cli doctor --manifest $manifest --profile $Profile
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    $syncArgs = @("sync", "--manifest", $manifest, "--target", $Target, "--profile", $Profile)
    if ($AwHome) {
        $syncArgs += @("--aw-home", $AwHome)
    }
    if ($Apply) {
        $syncArgs += "--apply"
    }

    python -m agentworkos.cli @syncArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
