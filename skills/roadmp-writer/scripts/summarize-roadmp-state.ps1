[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Roadmap
)

$ErrorActionPreference = "Stop"
$path = Resolve-Path -LiteralPath $Roadmap
$lines = Get-Content -LiteralPath $path -Encoding UTF8
$checked = ($lines | Where-Object { $_ -match '^\s*-\s+\[x\]' }).Count
$open = ($lines | Where-Object { $_ -match '^\s*-\s+\[ \]' }).Count
$total = $checked + $open

Write-Host "ROADMAP $($path.Path)"
Write-Host "TASKS done=$checked open=$open total=$total"
Write-Host ""
Write-Host "OPEN TASKS"
$lines | Where-Object { $_ -match '^\s*-\s+\[ \]' } | ForEach-Object {
    Write-Host $_
}
