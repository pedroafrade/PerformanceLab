param(
    [string]$ProjectId = "performancelab-private-alpha",
    [string]$InstanceId = "performancelab-alpha",
    [string]$DatabaseName = "performancelab",
    [string]$DatabaseUser = "performancelab_app",
    [string]$ConnectionName = "performancelab-private-alpha:europe-west1:performancelab-alpha",
    [string]$SecretId = "performancelab-alpha-database-url",
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

function Wait-SqlOperation {
    param(
        [string]$OperationName,
        [hashtable]$Headers
    )

    $operationUri = (
        "https://sqladmin.googleapis.com/sql/v1beta4/projects/" +
        "$ProjectId/operations/$OperationName"
    )

    do {
        Start-Sleep -Seconds 2
        $operation = Invoke-RestMethod `
            -Method Get `
            -Uri $operationUri `
            -Headers $Headers
    } while ($operation.status -ne "DONE")

    if ($operation.error) {
        throw "Cloud SQL did not complete the user operation."
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
$usersUri = (
    "https://sqladmin.googleapis.com/sql/v1beta4/projects/" +
    "$ProjectId/instances/$InstanceId/users"
)
$users = Invoke-RestMethod -Method Get -Uri $usersUri -Headers $headers
$userExists = @($users.items) | Where-Object { $_.name -eq $DatabaseUser }

if ($userExists -and -not $RotateExisting) {
    throw (
        "Database user $DatabaseUser already exists. " +
        "Use -RotateExisting only when deliberately replacing its password."
    )
}

Write-Host "Choose a unique password with at least 24 characters."
$securePassword = Read-Host "Database password" -AsSecureString
$secureConfirmation = Read-Host "Repeat the database password" -AsSecureString

$plainPassword = $null
$plainConfirmation = $null
$databaseUrl = $null
$encodedPayload = $null
$encodedPassword = $null
$userBody = $null
$secretBody = $null

try {
    $plainPassword = Get-PlainText $securePassword
    $plainConfirmation = Get-PlainText $secureConfirmation

    if ($plainPassword -cne $plainConfirmation) {
        throw "The two passwords do not match. No cloud resource was changed."
    }
    if ($plainPassword.Length -lt 24) {
        throw "The password must contain at least 24 characters. No cloud resource was changed."
    }
    if ($plainPassword -match "[\r\n]") {
        throw "The password cannot contain line breaks. No cloud resource was changed."
    }

    $userBody = @{
        name = $DatabaseUser
        password = $plainPassword
        type = "BUILT_IN"
    } | ConvertTo-Json -Compress

    if ($userExists) {
        $escapedUser = [Uri]::EscapeDataString($DatabaseUser)
        $operation = Invoke-RestMethod `
            -Method Put `
            -Uri "$usersUri?name=$escapedUser" `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $userBody
    }
    else {
        $operation = Invoke-RestMethod `
            -Method Post `
            -Uri $usersUri `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $userBody
    }

    Wait-SqlOperation -OperationName $operation.name -Headers $headers

    $encodedUser = [Uri]::EscapeDataString($DatabaseUser)
    $encodedPassword = [Uri]::EscapeDataString($plainPassword)
    $encodedDatabase = [Uri]::EscapeDataString($DatabaseName)
    $socketPath = [Uri]::EscapeDataString("/cloudsql/$ConnectionName")
    $databaseUrl = (
        "postgresql+psycopg://${encodedUser}:${encodedPassword}" +
        "@/${encodedDatabase}?host=${socketPath}"
    )

    $encodedPayload = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes($databaseUrl)
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
    Write-Host "Database access configured successfully."
    Write-Host "Secret version created: $versionName"
    Write-Host "The password and DATABASE_URL were not displayed or written to disk."
}
finally {
    $plainPassword = $null
    $plainConfirmation = $null
    $databaseUrl = $null
    $encodedPayload = $null
    $encodedPassword = $null
    $userBody = $null
    $secretBody = $null
    $accessToken = $null
    $securePassword = $null
    $secureConfirmation = $null
}
