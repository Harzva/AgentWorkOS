[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Roadmap
)

$ErrorActionPreference = "Stop"
$path = Resolve-Path -LiteralPath $Roadmap
$text = Get-Content -LiteralPath $path -Raw -Encoding UTF8
$lines = $text -split "`r?`n"

$checked = ($lines | Where-Object { $_ -match '^\s*-\s+\[x\]' }).Count
$open = ($lines | Where-Object { $_ -match '^\s*-\s+\[ \]' }).Count
$headings = ($lines | Where-Object { $_ -match '^##\s+' }).Count
$detailLinks = ($lines | Where-Object { $_ -match 'roadmpxx-tasks/' }).Count

$weakPhrases = @('基本完成', '应该可以', '后续优化', '差不多')
$weakHits = foreach ($phrase in $weakPhrases) {
    $matches = Select-String -LiteralPath $path -Pattern $phrase -SimpleMatch
    foreach ($match in $matches) {
        [pscustomobject]@{ Phrase = $phrase; Line = $match.LineNumber; Text = $match.Line.Trim() }
    }
}

[pscustomobject]@{
    Roadmap = $path.Path
    CheckedTasks = $checked
    OpenTasks = $open
    Headings = $headings
    DetailLinks = $detailLinks
    WeakPhraseHits = @($weakHits).Count
} | ConvertTo-Json -Depth 4

if (@($weakHits).Count -gt 0) {
    Write-Host "Weak phrases:" -ForegroundColor Yellow
    $weakHits | Format-Table -AutoSize
}
