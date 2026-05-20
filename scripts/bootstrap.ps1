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
    aw init --root .
    aw scan --workspace .
    aw lock --offline
    aw doctor
    if ($Apply) {
        aw sync --apply
    }
    else {
        aw sync
    }
}
finally {
    Pop-Location
}
