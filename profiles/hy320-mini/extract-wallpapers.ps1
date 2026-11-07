param(
    [string]$BackupZip = (Join-Path $env:USERPROFILE "Documents\Codex\2026-11-06\referenced-chatgpt-conversation-this-is-an-2\outputs\HY320_Launcher_Backup_2026-11-07.zip"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $BackupZip -PathType Leaf)) {
    throw "Backup ZIP not found: $BackupZip"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem

$destination = Join-Path $PSScriptRoot "wallpapers"
New-Item -ItemType Directory -Path $destination -Force | Out-Null

$expected = [ordered]@{
    "4pm_9pm.jpg" = 236421
    "6am_4pm.jpg" = 174144
    "9pm_6am.jpg" = 279878
    "custom_1793243537158.jpg" = 109597
    "Mario-Olhando-Canos.png" = 1842032
    "Mario-Peach-Toad.jpeg" = 446268
    "Mario-Peaches.png" = 2793239
    "Mario-Power-Fire.jpg" = 307444
    "Mario-Yoshi.png" = 2589260
}

$archive = [IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $BackupZip).Path)
$results = [System.Collections.Generic.List[object]]::new()

try {
    foreach ($name in $expected.Keys) {
        $entryName = "wallpapers/wallpapers/$name"
        $entry = $archive.GetEntry($entryName)

        if ($null -eq $entry) {
            throw "Missing entry in backup: $entryName"
        }
        if ($entry.Length -ne $expected[$name]) {
            throw "Unexpected backup size for $name. Expected $($expected[$name]), got $($entry.Length)."
        }

        $target = Join-Path $destination $name
        if ((Test-Path -LiteralPath $target) -and -not $Force) {
            throw "File already exists and was not overwritten: $target. Re-run with -Force only if replacement is intended."
        }

        $inputStream = $entry.Open()
        try {
            $outputStream = [IO.File]::Open($target, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::None)
            try {
                $inputStream.CopyTo($outputStream)
            }
            finally {
                $outputStream.Dispose()
            }
        }
        finally {
            $inputStream.Dispose()
        }

        $actual = (Get-Item -LiteralPath $target).Length
        if ($actual -ne $expected[$name]) {
            throw "Extracted file failed size verification: $target"
        }

        $hash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        $results.Add([pscustomobject]@{
            File = $name
            Bytes = $actual
            SHA256 = $hash
            Result = "OK"
        })
    }
}
finally {
    $archive.Dispose()
}

$results | Format-Table -AutoSize
Write-Host "Extracted and verified $($results.Count) wallpaper files into: $destination"
