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

$auth0Domain = (Read-Host "Auth0 domain (for example tenant.eu.auth0.com)").Trim()
$auth0Domain = $auth0Domain -replace "^https://", ""
$auth0Domain = $auth0Domain.TrimEnd("/")
if (-not $auth0Domain -or $auth0Domain -notmatch "^[A-Za-z0-9.-]+\.auth0\.com$") {
    throw "The Auth0 domain is invalid. No secret version was created."
}

$auth0ClientId = (Read-Host "Auth0 client ID").Trim()
if (-not $auth0ClientId -or $auth0ClientId -match "[\r\n]") {
    throw "The Auth0 client ID is empty or invalid. No secret version was created."
}

$secureAuth0ClientSecret = Read-Host "Auth0 client secret" -AsSecureString
$secureAuth0Confirmation = Read-Host "Repeat the Auth0 client secret" -AsSecureString

$plainClientSecret = $null
$plainConfirmation = $null
$plainAuth0ClientSecret = $null
$plainAuth0Confirmation = $null
$cookieSecret = $null
$oidcToml = $null
$encodedPayload = $null
$secretBody = $null
$randomGenerator = $null

try {
    $plainClientSecret = Get-PlainText $secureClientSecret
    $plainConfirmation = Get-PlainText $secureConfirmation

    if ($plainClientSecret -cne $plainConfirmation) {
        throw "The two client secrets do not match. No secret version was created."
    }
    if (-not $plainClientSecret -or $plainClientSecret -match "[\r\n]") {
        throw "The client secret is empty or invalid. No secret version was created."
    }

    $plainAuth0ClientSecret = Get-PlainText $secureAuth0ClientSecret
    $plainAuth0Confirmation = Get-PlainText $secureAuth0Confirmation
    if ($plainAuth0ClientSecret -cne $plainAuth0Confirmation) {
        throw "The two Auth0 client secrets do not match. No secret version was created."
    }
    if (-not $plainAuth0ClientSecret -or $plainAuth0ClientSecret -match "[\r\n]") {
        throw "The Auth0 client secret is empty or invalid. No secret version was created."
    }

    $cookieBytes = [byte[]]::new(32)
    $randomGenerator = [Security.Cryptography.RandomNumberGenerator]::Create()
    $randomGenerator.GetBytes($cookieBytes)
    $randomGenerator.Dispose()
    $randomGenerator = $null
    $cookieSecret = [Convert]::ToBase64String($cookieBytes)

    $oidcToml = @(
        'PERFORMANCELAB_ENV = "alpha"'
        ''
        '[auth]'
        ('redirect_uri = "{0}"' -f (ConvertTo-TomlString $redirectUri))
        ('cookie_secret = "{0}"' -f (ConvertTo-TomlString $cookieSecret))
        ''
        '[auth.google]'
        ('client_id = "{0}"' -f (ConvertTo-TomlString $clientId))
        ('client_secret = "{0}"' -f (ConvertTo-TomlString $plainClientSecret))
        'server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"'
        ''
        '[auth.email]'
        ('client_id = "{0}"' -f (ConvertTo-TomlString $auth0ClientId))
        ('client_secret = "{0}"' -f (ConvertTo-TomlString $plainAuth0ClientSecret))
        ('server_metadata_url = "https://{0}/.well-known/openid-configuration"' -f (ConvertTo-TomlString $auth0Domain))
        'client_kwargs = { "prompt" = "login" }'
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
    Write-Host "Google and email-code login configuration saved successfully."
    Write-Host "Secret version created: $versionName"
    Write-Host "Redirect URI: $redirectUri"
    Write-Host "The client secrets and cookie secret were not displayed or written to disk."
}
finally {
    if ($null -ne $randomGenerator) {
        $randomGenerator.Dispose()
    }
    if ($cookieBytes) {
        [Array]::Clear($cookieBytes, 0, $cookieBytes.Length)
    }
    $plainClientSecret = $null
    $plainConfirmation = $null
    $plainAuth0ClientSecret = $null
    $plainAuth0Confirmation = $null
    $cookieSecret = $null
    $oidcToml = $null
    $encodedPayload = $null
    $secretBody = $null
    $versions = $null
    $versionsProperty = $null
    $enabledVersions = $null
    $randomGenerator = $null
    $accessToken = $null
    $secureClientSecret = $null
    $secureConfirmation = $null
    $secureAuth0ClientSecret = $null
    $secureAuth0Confirmation = $null
}
