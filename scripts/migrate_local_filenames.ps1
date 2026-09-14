param([string]$ProcessedDirectory = "C:\MonsunBridge\data\processed")
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $ProcessedDirectory)) { throw "Processed directory not found: $ProcessedDirectory" }
Get-ChildItem -LiteralPath $ProcessedDirectory -Filter "DUMMY_*.csv" | ForEach-Object {
    $newName = $_.Name -replace "^DUMMY_", "MB_"
    Rename-Item -LiteralPath $_.FullName -NewName $newName
    Write-Host ("Renamed {0} -> {1}" -f $_.Name, $newName)
}
