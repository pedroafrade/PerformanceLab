param(
    [Parameter(Mandatory = $true)]
    [string]$Email,
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$Region = "europe-west1",
    [string]$JobName = "journal-alpha-invitations"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gcloud.cmd -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI was not found."
}

$normalizedEmail = $Email.Trim().ToLowerInvariant()
if (-not $normalizedEmail -or $normalizedEmail -notmatch "^[^@\s]+@[^@\s]+\.[^@\s]+$") {
    throw "Provide a valid email address."
}

$configuredProject = (& gcloud.cmd config get-value project 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $configuredProject -ne $ProjectId) {
    throw "The active Google Cloud project must be $ProjectId."
}

& gcloud.cmd run jobs execute $JobName `
    --project=$ProjectId `
    --region=$Region `
    --args=$normalizedEmail `
    --wait

if ($LASTEXITCODE -ne 0) {
    throw "The invitation job did not complete successfully."
}

Write-Host "Invitation created successfully for $normalizedEmail."
