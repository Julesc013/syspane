$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath 'D:\Projects\SysPane\syspane').Path
$rows = @()
foreach ($prefix in @('w-10-focus-idle','w-09-runtime-observation','w-08-large-commands')) {
$owned = (Resolve-Path -LiteralPath (Join-Path $workspace ('out\campaign\' + $prefix))).Path
if (-not $owned.StartsWith($workspace + '\out\campaign\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Owned path escaped workspace' }
$history = Join-Path $workspace ('build-support\evidence\' + $prefix + '-history')
foreach ($folder in Get-ChildItem -LiteralPath $owned -Directory) {
    $target = (Resolve-Path -LiteralPath $folder.FullName).Path
    if ([IO.Path]::GetDirectoryName($target) -ne $owned -or ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Unexpected cleanup target' }
    $files = @(Get-ChildItem -LiteralPath $target -Recurse -File)
    $entries = @()
    foreach ($file in $files) {
        if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Unexpected linked evidence' }
        $relative = [IO.Path]::GetRelativePath($target, $file.FullName)
        $archive = Join-Path (Join-Path $history $folder.Name) $relative
        if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw 'No preserved duplicate' }
        $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        if ($digest -ne (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash) { throw 'Duplicate differs' }
        $gitPath = [IO.Path]::GetRelativePath($workspace,$archive).Replace('\','/')
        $committed = git rev-parse "HEAD:$gitPath"
        if ($LASTEXITCODE -ne 0) { throw 'Not committed' }
        $blob = git hash-object --no-filters -- $archive
        if ($LASTEXITCODE -ne 0 -or $blob -ne $committed) { throw 'Committed bytes differ' }
        $entries += @{path=$relative; archive=$gitPath; sha256=$digest.ToLowerInvariant(); bytes=$file.Length}
    }
    if ($files.Count -eq 0) { throw 'Unexpected empty attempt' }
    $rows += @{owned=$owned; path=$target; files=$entries; bytes=($files | Measure-Object Length -Sum).Sum}
}
}
$receipt = Join-Path $workspace 'out\campaign\visibility-controls-extra-attempt-pruned-complete.json'
if (Test-Path -LiteralPath $receipt) { throw 'Receipt exists' }
$report = @{source=(git rev-parse HEAD); verified=$rows; bytes=($rows | Measure-Object bytes -Sum).Sum}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8NoBOM
foreach ($row in $rows) {
    $target = (Resolve-Path -LiteralPath $row.path).Path
    if ([IO.Path]::GetDirectoryName($target) -ne $row.owned) { throw 'Cleanup target changed' }
    Remove-Item -LiteralPath $target -Recurse -Force
}
"Verified committed duplicates removed: $($rows.Count); bytes: $($report.bytes)"


