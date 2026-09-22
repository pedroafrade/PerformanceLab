param(
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$Region = "europe-west1",
    [string]$Repository = "performancelab",
    [string]$ImageName = "application"
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedCommand {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed. The image was not approved for deployment."
    }
}

foreach ($commandName in @("git", "gcloud.cmd", "python")) {
    if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
        throw "$commandName was not found. Open a new PowerShell window and try again."
    }
}

$configuredProject = (& gcloud.cmd config get-value project 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $configuredProject -ne $ProjectId) {
    throw "The active Google Cloud project must be $ProjectId."
}

$branch = (& git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne "main") {
    throw "Publish only from the main branch."
}

$workingTree = & git status --porcelain --untracked-files=all
if ($LASTEXITCODE -ne 0 -or $workingTree) {
    throw "The Git working tree must be clean before publishing an image."
}

Invoke-CheckedCommand "git" @("fetch", "--quiet", "origin", "main")

$commit = (& git rev-parse HEAD).Trim()
$remoteCommit = (& git rev-parse origin/main).Trim()
if (
    $LASTEXITCODE -ne 0 `
    -or $commit -notmatch "^[0-9a-f]{40}$" `
    -or $commit -ne $remoteCommit
) {
    throw "The local main commit must match origin/main before publishing."
}

$imageBase = "$Region-docker.pkg.dev/$ProjectId/$Repository/$ImageName"
$imageTag = "${imageBase}:${commit}"

Write-Host "Building the exact main commit in Google Cloud."
Write-Host "This can take several minutes."

Invoke-CheckedCommand "gcloud.cmd" @(
    "builds",
    "submit",
    ".",
    "--config=infra/google-alpha/cloudbuild.yaml",
    "--substitutions=_IMAGE=$imageTag,_VCS_REF=$commit",
    "--project=$ProjectId",
    "--region=$Region",
    "--quiet"
)

$digest = (& gcloud.cmd artifacts docker images describe `
    $imageTag `
    "--project=$ProjectId" `
    "--format=value(image_summary.digest)").Trim()

if ($LASTEXITCODE -ne 0 -or $digest -notmatch "^sha256:[0-9a-f]{64}$") {
    throw "The published image digest could not be confirmed."
}

$immutableReference = "${imageBase}@${digest}"

try {
    $env:DEPLOYMENT_IMAGE_REFERENCE = $immutableReference
    Invoke-CheckedCommand "python" @(
        "scripts/check_alpha_image_reference.py"
    )
}
finally {
    Remove-Item Env:DEPLOYMENT_IMAGE_REFERENCE -ErrorAction SilentlyContinue
}

Write-Host "Candidate image published successfully."
Write-Host "Commit: $commit"
Write-Host "Immutable image reference:"
Write-Host $immutableReference
