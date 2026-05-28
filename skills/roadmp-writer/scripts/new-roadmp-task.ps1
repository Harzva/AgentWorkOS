[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TasksDir,
    [Parameter(Mandatory = $true)]
    [int]$Number,
    [Parameter(Mandatory = $true)]
    [string]$Slug,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [string]$Template = ""
)

$ErrorActionPreference = "Stop"
$dir = Resolve-Path -LiteralPath $TasksDir
$safeSlug = $Slug.ToLowerInvariant() -replace '[^a-z0-9\-]+', '-'
$fileName = ('{0:D2}-{1}.md' -f $Number, $safeSlug)
$target = Join-Path $dir $fileName

if (Test-Path -LiteralPath $target) {
    throw "task file already exists: $target"
}

if ($Template) {
    $templatePath = Resolve-Path -LiteralPath $Template
}
else {
    $templatePath = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\templates\task-detail.md')
}

$content = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8
$content = $content.Replace('{{NUMBER}}', ('{0:D2}' -f $Number)).Replace('{{TITLE}}', $Title).Replace('{{GOAL}}', 'TBD')
Set-Content -LiteralPath $target -Value $content -Encoding UTF8
Write-Host "wrote: $target"
