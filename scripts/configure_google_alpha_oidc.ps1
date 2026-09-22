param(
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$ApplicationUrl = "https://performancelab-alpha-mrpmgz34ba-ew.a.run.app",
    [string]$SecretId = "performancelab-alpha-oidc-toml",
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

function ConvertTo-TomlString {
    param([string]$Value)

    return $Value.Replace("\", "\\").Replace('"', '\"')
}

if (-not (Get-Command gcloud.cmd -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI was not found. Open a new PowerShell window and try again."
}

$configuredProject = (& gcloud.cmd config get-value project 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $configuredProject -ne $ProjectId) {
    throw "The active Google Cloud project must be $ProjectId."
}

$applicationUri = $null
if (-not [Uri]::TryCreate($ApplicationUrl, [UriKind]::Absolute, [ref]$applicationUri)) {
    throw "ApplicationUrl must be a valid absolute URL."
}
if ($applicationUri.Scheme -ne "https" -or $applicationUri.Query -or $applicationUri.Fragment) {
    throw "ApplicationUrl must be an HTTPS address without a query or fragment."
}

$normalizedUrl = $ApplicationUrl.TrimEnd("/")
$redirectUri = "$normalizedUrl/oauth2callback"
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
        "An enabled OIDC secret version already exists. " +
        "Use -RotateExisting only when deliberately replacing the credentials."
    )
}

$clientId = (Read-Host "Google OAuth client ID").Trim()
if (-not $clientId -or $clientId -match "[\r\n]") {
    throw "The client ID is empty or invalid. No secret version was created."
}

$secureClientSecret = Read-Host "Google OAuth client secret" -AsSecureString
$secureConfirmation = Read-Host "Repeat the Google OAuth client secret" -AsSecureString

$plainClientSecret = $null
$plainConfirmation = $null
$cookieSecret = $null
$oidcToml = $null
$encodedPayload = $null
$secretBody = $null

try {
    $plainClientSecret = Get-PlainText $secureClientSecret
    $plainConfirmation = Get-PlainText $secureConfirmation

    if ($plainClientSecret -cne $plainConfirmation) {
        throw "The two client secrets do not match. No secret version was created."
    }
    if (-not $plainClientSecret -or $plainClientSecret -match "[\r\n]") {
        throw "The client secret is empty or invalid. No secret version was created."
    }

    $cookieBytes = [byte[]]::new(32)
    [Security.Cryptography.RandomNumberGenerator]::Fill($cookieBytes)
    $cookieSecret = [Convert]::ToBase64String($cookieBytes)

    $oidcToml = @(
        'PERFORMANCELAB_ENV = "alpha"'
        ''
        '[auth]'
        ('redirect_uri = "{0}"' -f (ConvertTo-TomlString $redirectUri))
        ('cookie_secret = "{0}"' -f (ConvertTo-TomlString $cookieSecret))
        ('client_id = "{0}"' -f (ConvertTo-TomlString $clientId))
        ('client_secret = "{0}"' -f (ConvertTo-TomlString $plainClientSecret))
        'server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"'
        ''
    ) -join "`n"

    $encodedPayload = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes($oidcToml)
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
    Write-Host "Google login configuration saved successfully."
    Write-Host "Secret version created: $versionName"
    Write-Host "Redirect URI: $redirectUri"
    Write-Host "The client secret and cookie secret were not displayed or written to disk."
}
finally {
    if ($cookieBytes) {
        [Array]::Clear($cookieBytes, 0, $cookieBytes.Length)
    }
    $plainClientSecret = $null
    $plainConfirmation = $null
    $cookieSecret = $null
    $oidcToml = $null
    $encodedPayload = $null
    $secretBody = $null
    $versions = $null
    $versionsProperty = $null
    $enabledVersions = $null
    $accessToken = $null
    $secureClientSecret = $null
    $secureConfirmation = $null
}
