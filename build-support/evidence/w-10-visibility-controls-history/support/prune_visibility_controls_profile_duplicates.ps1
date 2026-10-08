$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath 'D:\Projects\SysPane\syspane').Path
$blobs = @{}
foreach ($line in git ls-tree -r HEAD -- build-support/evidence) {
    if ($line -match '^\d+ blob ([0-9a-f]+)\t(.+)$' -and -not $blobs.ContainsKey($Matches[1])) { $blobs[$Matches[1]] = $Matches[2] }
}
if ($LASTEXITCODE -ne 0) { throw 'Cannot read committed tree' }
$rows = @()
foreach ($profile in @('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp')) {
    $owned = (Resolve-Path -LiteralPath (Join-Path $workspace ('out\campaign\'+$profile))).Path
    if (-not $owned.StartsWith($workspace+'\out\campaign\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected root' }
    foreach ($file in Get-ChildItem -LiteralPath $owned -Recurse -File) {
        if ($file.Extension -notin @('.zip','.json')) { continue }
        if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked candidate' }
        $parent = $file.Directory
        while ($parent.FullName -ne $owned) {
            if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked ancestor' }
            $parent = $parent.Parent
        }
        $blob = git hash-object --no-filters -- $file.FullName
        if ($LASTEXITCODE -ne 0) { throw 'Cannot hash candidate' }
        if (-not $blobs.ContainsKey($blob)) { continue }
        $archive = Join-Path $workspace $blobs[$blob]
        if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { continue }
        $actual = git hash-object --no-filters -- $archive
        if ($LASTEXITCODE -ne 0 -or $actual -ne $blob) { throw 'Committed archive changed' }
        $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        if ($digest -ne (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash) { throw 'Bytes differ' }
        $rows += @{path=$file.FullName; owned=$owned; archive=$blobs[$blob]; sha256=$digest.ToLowerInvariant(); bytes=$file.Length}
    }
}
$receipt = Join-Path $workspace 'out\campaign\visibility-controls-profile-pruned-duplicates.json'
if (Test-Path -LiteralPath $receipt) { throw 'Receipt exists' }
$report = @{source=(git rev-parse HEAD); verified=$rows; bytes=($rows | Measure-Object bytes -Sum).Sum}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8NoBOM
foreach ($row in $rows) {
    $target = (Resolve-Path -LiteralPath $row.path).Path
    if (-not $target.StartsWith($row.owned+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Target escaped root' }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256) { throw 'Candidate changed' }
    Remove-Item -LiteralPath $target -Force
}
"Verified committed profile duplicates removed: $($rows.Count); bytes: $($report.bytes)"
