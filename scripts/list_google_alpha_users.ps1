param(
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$Region = "europe-west1",
    [string]$JobName = "journal-alpha-invitations"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gcloud.cmd -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI was not found."
}

$configuredProject = (& gcloud.cmd config get-value project 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $configuredProject -ne $ProjectId) {
    throw "The active Google Cloud project must be $ProjectId."
}

$executionOutput = & gcloud.cmd run jobs execute $JobName `
    --project=$ProjectId `
    --region=$Region `
    --args=--list `
    --wait `
    --quiet `
    "--format=value(metadata.name)"

if ($LASTEXITCODE -ne 0) {
    throw "The invitation listing job did not complete successfully."
}

$executionName = (
    $executionOutput |
        Where-Object { $_ -match "^$([regex]::Escape($JobName))-[a-z0-9]+$" } |
        Select-Object -Last 1
)

if (-not $executionName) {
    throw "The invitation listing execution name could not be determined."
}

Write-Host "Private alpha invitations:"
Write-Host ""

& gcloud.cmd beta run jobs executions logs read $executionName `
    --project=$ProjectId `
    --region=$Region `
    --limit=200 `
    --order=asc

if ($LASTEXITCODE -ne 0) {
    throw "The invitation list could not be read from the job logs."
}
