param([string]$OutputDirectory = ".\data\official")
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$datasets = @(
    @{ Name = "dosm_lfs_district.csv"; Url = "https://storage.dosm.gov.my/labour/lfs_district.csv" },
    @{ Name = "dosm_employment_sector.csv"; Url = "https://storage.dosm.gov.my/labour/employment_sector.csv" },
    @{ Name = "dosm_hh_income_district.csv"; Url = "https://storage.dosm.gov.my/hies/hh_income_district.csv" },
    @{ Name = "dosm_population_district.csv"; Url = "https://storage.dosm.gov.my/population/population_district.csv" },
    @{ Name = "dof_fish_landings.csv"; Url = "https://storage.data.gov.my/agriculture/fish_landings.csv" }
)
foreach ($dataset in $datasets) {
    $destination = Join-Path $OutputDirectory $dataset.Name
    Write-Host ("Downloading {0}" -f $dataset.Name)
    Invoke-WebRequest -Uri $dataset.Url -OutFile $destination
}
Write-Host "Official CSV downloads completed. Record download dates and hashes before preprocessing."
