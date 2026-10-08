$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath 'D:\Projects\SysPane\syspane').Path
$owned = (Resolve-Path -LiteralPath (Join-Path $workspace 'out\campaign')).Path
if ($owned -ne (Join-Path $workspace 'out\campaign')) { throw 'Unexpected owned root' }
$known = @{}
$rows = @()
foreach ($file in Get-ChildItem -LiteralPath $owned -Filter 'source-inputs.zip' -Recurse -File | Sort-Object FullName) {
    $target = (Resolve-Path -LiteralPath $file.FullName).Path
    if (-not $target.StartsWith($owned + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Escaped owned root' }
    if ($target.StartsWith((Join-Path $owned 'w-10-theme-history') + '\', [StringComparison]::OrdinalIgnoreCase)) { continue }
    if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked input archive' }
    $result = Join-Path $file.DirectoryName 'result.json'
    if (-not (Test-Path -LiteralPath $result)) { continue }
    $value = Get-Content -LiteralPath $result -Raw | ConvertFrom-Json
    $digest = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($value.source_archive_sha256 -ne $digest) { continue }
    if (-not $known.ContainsKey($digest)) { $known[$digest] = $target; continue }
    $rows += @{removed=$target; retained=$known[$digest]; sha256=$digest; bytes=$file.Length; result=$result}
}
$receipt = Join-Path $owned 'theme-history-deduplicated-old-sources.json'
if (Test-Path -LiteralPath $receipt) { throw 'Receipt exists' }
@{source=(git rev-parse HEAD); scope='Only redundant older source-inputs.zip files; results and current checkpoint untouched. Restore by copying retained to removed.'; verified=$rows; bytes=($rows | Measure-Object bytes -Sum).Sum} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receipt -Encoding utf8NoBOM
foreach ($row in $rows) {
    $target = (Resolve-Path -LiteralPath $row.removed).Path
    if (-not $target.StartsWith($owned + '\', [StringComparison]::OrdinalIgnoreCase) -or $target -eq $row.retained) { throw 'Invalid duplicate target' }
    if ((Get-FileHash -LiteralPath $row.retained -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256 -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256) { throw 'Archive changed' }
    Remove-Item -LiteralPath $target
}
"Removed redundant older archives: $($rows.Count); bytes: $(($rows | Measure-Object bytes -Sum).Sum)"
