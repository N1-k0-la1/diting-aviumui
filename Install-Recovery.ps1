# SPDX-License-Identifier: Apache-2.0
# Portable testing-release installer. Default is read-only; never formats userdata or installs the OTA.
param(
    [Parameter(Mandatory=$true)][string]$Serial,
    [ValidateSet('gms','vanilla')][string]$Flavour='gms',
    [string]$FastbootPath='fastboot.exe',
    [switch]$FlashRecovery
)
$ErrorActionPreference='Stop'
if ($Serial -notmatch '^[A-Za-z0-9._:-]+$') { throw 'Invalid target serial' }
$manifestRelease = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'MANIFEST.json') -Raw | ConvertFrom-Json
$candidatesRelease = @($manifestRelease.candidates | Where-Object flavour -CEQ $Flavour)
if ($candidatesRelease.Count -ne 1) { throw 'Missing matching candidate' }
$candidateRelease=$candidatesRelease[0]
$assetRowsRelease=@($manifestRelease.assets | Where-Object flavour -CEQ $Flavour)
$assetNamesRelease=@($assetRowsRelease.path | Sort-Object)
$expectedNamesRelease=@($candidateRelease.file) + @('boot','dtbo','vendor_boot','recovery','vbmeta','vbmeta_system' | ForEach-Object { "$Flavour/$_.img" })
if (($assetNamesRelease -join '|') -cne (($expectedNamesRelease | Sort-Object) -join '|')) { throw 'Unexpected or incomplete asset set' }
foreach ($assetRelease in $assetRowsRelease) {
    $pathRelease=Join-Path $PSScriptRoot $assetRelease.path
    if ((Get-Item -LiteralPath $pathRelease).Length -ne $assetRelease.bytes -or
        (Get-FileHash -LiteralPath $pathRelease -Algorithm SHA256).Hash.ToLowerInvariant() -cne $assetRelease.sha256) {
        throw "Asset size/hash mismatch: $($assetRelease.path)"
    }
}
function Invoke-ReleaseFastboot([string[]]$Arguments) {
    $argumentsRelease=@('-s',$Serial)+$Arguments
    foreach ($argumentRelease in $argumentsRelease) {
        if ($argumentRelease -match '["\r\n]' -or $argumentRelease.EndsWith('\')) { throw 'Unexpected process argument' }
    }
    $infoRelease=New-Object System.Diagnostics.ProcessStartInfo
    $infoRelease.FileName=$FastbootPath
    $infoRelease.Arguments=(($argumentsRelease | ForEach-Object { '"'+$_+'"' }) -join ' ')
    $infoRelease.UseShellExecute=$false
    $infoRelease.CreateNoWindow=$true
    $infoRelease.RedirectStandardOutput=$true
    $infoRelease.RedirectStandardError=$true
    $processRelease=[Diagnostics.Process]::Start($infoRelease)
    $stdoutRelease=$processRelease.StandardOutput.ReadToEndAsync()
    $stderrRelease=$processRelease.StandardError.ReadToEndAsync()
    if (-not $processRelease.WaitForExit(60000)) {
        $processRelease.Kill()
        throw 'Fastboot timed out. Preserve the current phone mode and stop further writes.'
    }
    $outputRelease=$stdoutRelease.Result+"`n"+$stderrRelease.Result
    if ($processRelease.ExitCode -ne 0) { throw "Fastboot failed: $($Arguments -join ' ')`n$outputRelease" }
    return $outputRelease
}
function Read-ReleaseVariable([string]$Name) {
    $outputRelease=Invoke-ReleaseFastboot @('getvar',$Name)
    $matchRelease=[regex]::Match($outputRelease,'(?m)^(?:\(bootloader\)\s*)?' + [regex]::Escape($Name) + ':\s*(\S+)')
    if (-not $matchRelease.Success) { throw "Cannot parse Fastboot variable: $Name" }
    return $matchRelease.Groups[1].Value
}
function Assert-ReleaseTarget([string]$ExpectedSlot) {
    if ((Read-ReleaseVariable 'product') -cne 'diting' -or
        (Read-ReleaseVariable 'unlocked') -cne 'yes' -or
        (Read-ReleaseVariable 'is-userspace') -cne 'no' -or
        (Read-ReleaseVariable 'current-slot') -cne $ExpectedSlot) {
        throw 'Target, unlock, mode or slot changed; stop before further writes'
    }
}
$slotRelease=Read-ReleaseVariable 'current-slot'
if ($slotRelease -cnotmatch '^[ab]$') { throw 'Unknown current A/B slot' }
Assert-ReleaseTarget $slotRelease
$imagesRelease=@()
foreach ($nameRelease in @('boot','dtbo','vendor_boot','recovery','vbmeta','vbmeta_system')) {
    $partitionRelease=$nameRelease + '_' + $slotRelease
    $sizeRelease=Read-ReleaseVariable ('partition-size:'+$partitionRelease)
    $rowRelease=@($assetRowsRelease | Where-Object path -CEQ "$Flavour/$nameRelease.img")
    if ($rowRelease.Count -ne 1 -or $sizeRelease -notmatch '^0x[0-9a-fA-F]+$' -or
        $rowRelease[0].bytes -gt [Convert]::ToInt64($sizeRelease.Substring(2),16) -or
        (Read-ReleaseVariable ('partition-type:'+$partitionRelease)) -cne 'raw') {
        throw "Unexpected partition layout or oversized image: $partitionRelease"
    }
    $imagesRelease += [pscustomobject]@{partition=$partitionRelease;asset=$rowRelease[0]}
}
if (-not $FlashRecovery) {
    Write-Output "Verified $Flavour assets and unlocked diting current slot $slotRelease. No flash, erase or reboot performed."
    exit 0
}
foreach ($imageRelease in $imagesRelease) {
    Assert-ReleaseTarget $slotRelease
    $imagePathRelease=Join-Path $PSScriptRoot $imageRelease.asset.path
    if ((Get-FileHash -LiteralPath $imagePathRelease -Algorithm SHA256).Hash.ToLowerInvariant() -cne $imageRelease.asset.sha256) { throw 'Image changed after verification' }
    Write-Output (Invoke-ReleaseFastboot @('flash',$imageRelease.partition,$imagePathRelease))
}
$null=Invoke-ReleaseFastboot @('reboot','bootloader')
Assert-ReleaseTarget $slotRelease
Write-Output (Invoke-ReleaseFastboot @('reboot','recovery'))
Write-Output 'Wait for AviumUI Recovery. Follow INSTALL.md to clean install the matching full OTA before booting system.'
Write-Output 'Userdata has NOT been formatted and the OTA has NOT been installed. Do not relock the bootloader.'
