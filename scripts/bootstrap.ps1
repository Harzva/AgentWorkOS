[CmdletBinding()]
param(
    [string]$Root = ".",
    [ValidateSet("base", "codex", "just-ddl", "full")]
    [string]$Profile = "codex",
    [ValidateSet("codex", "claude-code", "claude", "all")]
    [string]$Target = "codex",
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
    aw doctor --profile $Profile
    if ($Apply) {
        aw sync --profile $Profile --target $Target --apply
    }
    else {
        aw sync --profile $Profile --target $Target
    }
}
finally {
    Pop-Location
}
