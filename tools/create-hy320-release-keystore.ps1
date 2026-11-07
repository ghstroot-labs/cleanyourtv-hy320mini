# Create the permanent private signing key for the GHSTROOT HY320 Mini launcher.
# The keystore and its Base64 transfer file are written outside the repository.
# The password is entered securely and is never saved by this script.

$ErrorActionPreference = 'Stop'

$directory = Join-Path $env:LOCALAPPDATA 'GHSTROOT\CleanYourTV\Signing'
$keystorePath = Join-Path $directory 'cleanyourtv-hy320mini-release.p12'
$base64Path = Join-Path $directory 'cleanyourtv-hy320mini-release.p12.base64.txt'
$keyAlias = 'ghstroot-hy320mini-release'

New-Item -ItemType Directory -Path $directory -Force | Out-Null

if (Test-Path -LiteralPath $keystorePath) {
    throw "A signing keystore already exists at $keystorePath. This script will not overwrite it."
}
if (Test-Path -LiteralPath $base64Path) {
    throw "A Base64 file already exists at $base64Path. This script will not overwrite it."
}

$keytool = $null
if ($env:JAVA_HOME) {
    $candidate = Join-Path $env:JAVA_HOME 'bin\keytool.exe'
    if (Test-Path -LiteralPath $candidate) { $keytool = $candidate }
}
if (-not $keytool) {
    $candidate = 'C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe'
    if (Test-Path -LiteralPath $candidate) { $keytool = $candidate }
}
if (-not $keytool) {
    $command = Get-Command keytool.exe -ErrorAction SilentlyContinue
    if ($command) { $keytool = $command.Source }
}
if (-not $keytool) {
    throw 'keytool.exe was not found. Install/use JDK 17 (Android Studio includes one) or set JAVA_HOME.'
}

function ConvertFrom-SecureStringPlain {
    param([Parameter(Mandatory = $true)][Security.SecureString]$Value)
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value)
    try {
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

$password = Read-Host 'Create a strong keystore password (minimum 16 characters)' -AsSecureString
$confirmation = Read-Host 'Confirm the keystore password' -AsSecureString
$plainPassword = ConvertFrom-SecureStringPlain $password
$confirmPassword = ConvertFrom-SecureStringPlain $confirmation

if ($plainPassword.Length -lt 16) {
    $plainPassword = $null
    $confirmPassword = $null
    throw 'Use a password with at least 16 characters.'
}
if ($plainPassword -cne $confirmPassword) {
    $plainPassword = $null
    $confirmPassword = $null
    throw 'The passwords do not match. No key was created.'
}
$confirmPassword = $null

try {
    # PKCS#12 uses the same password for the keystore and its single signing key.
    $env:ANDROID_KEYSTORE_PASSWORD = $plainPassword
    $keytoolArgs = @(
        '-genkeypair',
        '-v',
        '-storetype', 'PKCS12',
        '-keystore', $keystorePath,
        '-alias', $keyAlias,
        '-keyalg', 'RSA',
        '-keysize', '4096',
        '-validity', '10000',
        '-dname', 'CN=GHSTROOT Labs, OU=HY320 Mini, O=GHSTROOT Labs, C=BR',
        '-storepass:env', 'ANDROID_KEYSTORE_PASSWORD',
        '-keypass:env', 'ANDROID_KEYSTORE_PASSWORD'
    )
    & $keytool @keytoolArgs
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $keystorePath)) {
        throw 'keytool failed to create the signing keystore.'
    }

    $verifyArgs = @(
        '-list', '-keystore', $keystorePath, '-storetype', 'PKCS12',
        '-storepass:env', 'ANDROID_KEYSTORE_PASSWORD', '-alias', $keyAlias
    )
    & $keytool @verifyArgs | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw 'The new keystore could not be verified.'
    }
}
catch {
    if (Test-Path -LiteralPath $keystorePath) {
        Remove-Item -LiteralPath $keystorePath -Force
    }
    throw
}
finally {
    Remove-Item Env:ANDROID_KEYSTORE_PASSWORD -ErrorAction SilentlyContinue
    $plainPassword = $null
    $password = $null
    $confirmation = $null
}

$bytes = [IO.File]::ReadAllBytes($keystorePath)
$base64 = [Convert]::ToBase64String($bytes)
[IO.File]::WriteAllText($base64Path, $base64, [Text.Encoding]::ASCII)

[pscustomobject]@{
    Keystore = $keystorePath
    Base64File = $base64Path
    Alias = $keyAlias
    KeystoreSHA256 = (Get-FileHash -LiteralPath $keystorePath -Algorithm SHA256).Hash
    Note = 'Keep an offline backup of the .p12 file. Do not commit either file to Git.'
} | Format-List

Write-Host 'Create these three repository Actions secrets:'
Write-Host '  ANDROID_KEYSTORE_BASE64   = the complete contents of the Base64 file'
Write-Host '  ANDROID_KEYSTORE_PASSWORD = the password entered above'
Write-Host "  ANDROID_KEY_ALIAS         = $keyAlias"
Write-Host 'The workflow uses the keystore password for the key password as well.'
