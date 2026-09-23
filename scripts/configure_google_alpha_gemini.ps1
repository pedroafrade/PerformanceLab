param(
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$SecretId = "performancelab-alpha-gemini-api-key",
    [switch]$RotateExisting
)

$ErrorActionPreference = "Stop"

function Get-PlainText {
    param([Security.SecureString]$SecureValue)

    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

if (-not (Get-Command gcloud.cmd -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI was not found. Open a new PowerShell window and try again."
}

$configuredProject = (& gcloud.cmd config get-value project 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $configuredProject -ne $ProjectId) {
    throw "The active Google Cloud project must be $ProjectId."
}

$accessToken = (& gcloud.cmd auth print-access-token 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or -not $accessToken) {
    throw "Google Cloud authentication is unavailable. Run gcloud.cmd auth login first."
}

$headers = @{ Authorization = "Bearer $accessToken" }
$versionsUri = (
    "https://secretmanager.googleapis.com/v1/projects/" +
    "$ProjectId/secrets/$SecretId/versions?filter=state%3AENABLED"
)
$versions = Invoke-RestMethod -Method Get -Uri $versionsUri -Headers $headers
$enabledVersions = @()
$versionsProperty = $null

if ($null -ne $versions) {
    $versionsProperty = $versions.PSObject.Properties["versions"]
}

if ($null -ne $versionsProperty -and $null -ne $versionsProperty.Value) {
    $enabledVersions = @(
        $versionsProperty.Value |
            Where-Object { $null -ne $_ -and $_.state -eq "ENABLED" }
    )
}

if ($enabledVersions.Count -gt 0 -and -not $RotateExisting) {
    throw (
        "An enabled Gemini secret version already exists. " +
        "Use -RotateExisting only when deliberately replacing the API key."
    )
}

$secureApiKey = Read-Host "Gemini API key" -AsSecureString
$secureConfirmation = Read-Host "Repeat the Gemini API key" -AsSecureString

$plainApiKey = $null
$plainConfirmation = $null
$encodedPayload = $null
$secretBody = $null

try {
    $plainApiKey = Get-PlainText $secureApiKey
    $plainConfirmation = Get-PlainText $secureConfirmation

    if ($plainApiKey -cne $plainConfirmation) {
        throw "The two API keys do not match. No secret version was created."
    }
    if (-not $plainApiKey -or $plainApiKey -match "[\r\n]") {
        throw "The API key is empty or invalid. No secret version was created."
    }

    $encodedPayload = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes($plainApiKey)
    )
    $secretBody = @{
        payload = @{ data = $encodedPayload }
    } | ConvertTo-Json -Compress -Depth 3
    $secretUri = (
        "https://secretmanager.googleapis.com/v1/projects/" +
        "$ProjectId/secrets/${SecretId}:addVersion"
    )

    $secretVersion = Invoke-RestMethod `
        -Method Post `
        -Uri $secretUri `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $secretBody

    $versionName = ($secretVersion.name -split "/")[-1]
    Write-Host "Gemini configuration saved successfully."
    Write-Host "Secret version created: $versionName"
    Write-Host "The API key was not displayed or written to disk."
}
finally {
    $plainApiKey = $null
    $plainConfirmation = $null
    $encodedPayload = $null
    $secretBody = $null
    $versions = $null
    $versionsProperty = $null
    $enabledVersions = $null
    $accessToken = $null
    $secureApiKey = $null
    $secureConfirmation = $null
}
