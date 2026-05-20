[CmdletBinding()]
param(
    [string]$Root = ".",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$repo = Resolve-Path -LiteralPath $Root
Push-Location $repo
try {
    python -m pip install -e .
    awos init --root .
    awos scan --workspace .
    awos lock --offline
    awos doctor
    if ($Apply) {
        awos sync --apply
    }
    else {
        awos sync
    }
}
finally {
    Pop-Location
}
