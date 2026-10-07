$ErrorActionPreference = 'Stop'
$repoRoot = (Get-Location).Path
if ($repoRoot -ne 'D:\Projects\SysPane\syspane') { throw 'Unexpected checkout' }
$ownedRoot = (Resolve-Path -LiteralPath (Join-Path $repoRoot 'out/campaign/windows-x64-gcc15')).Path
function CheckedPath([string] $candidate) {
    $resolved = (Resolve-Path -LiteralPath $candidate).Path
    if (-not $resolved.StartsWith($ownedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside owned smoke root' }
    $item = Get-Item -LiteralPath $resolved
    while ($item.FullName -ne $ownedRoot) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point' }
        if ($item -is [IO.FileInfo]) { $item = $item.Directory } else { $item = $item.Parent }
        if ($null -eq $item) { throw 'Outside owned root' }
    }
    return $resolved
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$records = @(); $total = 0
foreach ($directory in (Get-ChildItem -LiteralPath $ownedRoot -Directory -Filter 'smoke-*')) {
    if ($total -ge 80MB) { break }
    $candidate = Join-Path $directory.FullName 'relocated/bin/SysPane.ModelSmoke.exe'
    if (-not (Test-Path -LiteralPath $candidate)) { continue }
    $candidate = CheckedPath $candidate
    $owner = Get-Content -Raw -LiteralPath (CheckedPath (Join-Path $directory.FullName '.syspane-owner.json')) | ConvertFrom-Json
    $report = Get-Content -Raw -LiteralPath (CheckedPath (Join-Path $directory.FullName 'result.json')) | ConvertFrom-Json
    if ($owner.owner -ne 'W-26' -or $owner.profile -ne 'windows-x64-gcc15' -or $report.status -ne 'pass') { throw 'Unexpected smoke ownership/status' }
    if ([IO.Path]::GetFileName($report.archive) -ne $report.archive) { throw 'Invalid package basename' }
    $archive = CheckedPath (Join-Path $directory.FullName $report.archive)
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $report.archive_sha256) { throw 'Archive changed' }
    $digest = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $report.payload_sha256) { throw 'Payload changed' }
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        $entry = $zip.GetEntry('bin/SysPane.ModelSmoke.exe')
        if ($null -eq $entry) { throw 'Missing archived payload' }
        $stream = $entry.Open(); $hash = [Security.Cryptography.SHA256]::Create()
        try { $archivedDigest = [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-','').ToLowerInvariant() }
        finally { $stream.Dispose(); $hash.Dispose() }
        if ($archivedDigest -ne $digest) { throw 'Archived bytes differ' }
    } finally { $zip.Dispose() }
    $length = (Get-Item -LiteralPath $candidate).Length
    $records += @{removed=$candidate; bytes=$length; sha256=$digest; retained_archive=$archive; archive_sha256=$report.archive_sha256; member='bin/SysPane.ModelSmoke.exe'}
    Remove-Item -LiteralPath $candidate
    $total += $length
}
@{source_base=(git rev-parse HEAD); reason='Remove only byte-identical unpacked copies of completed owned development smoke packages; retain package archives and original reports'; reclaimed_bytes=$total; copies=$records} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'out/campaign/native-settings-smoke-reclamation.json' -Encoding utf8
Write-Output "Reclaimed $total bytes in $($records.Count) archived smoke payload copies."
