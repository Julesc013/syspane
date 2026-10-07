$ErrorActionPreference = 'Stop'
$repoRoot = (Get-Location).Path
if ($repoRoot -ne 'D:\Projects\SysPane\syspane') { throw 'Unexpected checkout' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'out/campaign'))
$retained = @{}
foreach ($relative in (git ls-files 'build-support/evidence/**/source-inputs.zip')) {
    $archive = (Resolve-Path -LiteralPath (Join-Path $repoRoot $relative)).Path
    $key = [IO.Path]::GetFileName([IO.Path]::GetDirectoryName($archive))
    if (-not $retained.ContainsKey($key)) { $retained[$key] = @() }
    $retained[$key] += $relative
}
$records = @()
foreach ($file in (Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Filter 'source-inputs.zip')) {
    $candidate = [IO.Path]::GetFullPath($file.FullName)
    if (-not $candidate.StartsWith($sourceRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside owned output' }
    $parent = $file.Directory
    while ($parent.FullName -ne $sourceRoot) {
        if (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point in output path' }
        $parent = $parent.Parent
        if ($null -eq $parent) { throw 'Outside root' }
    }
    if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse archive' }
    if (-not $retained.ContainsKey($file.Directory.Name)) { continue }
    $digest = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
    foreach ($relative in $retained[$file.Directory.Name]) {
        $archive = (Resolve-Path -LiteralPath (Join-Path $repoRoot $relative)).Path
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $digest) { continue }
        git diff --quiet HEAD -- $relative
        if ($LASTEXITCODE -ne 0) { throw 'Retained archive changed from commit' }
        $records += @{ removed=$candidate; retained=$relative; sha256=$digest.ToLowerInvariant(); bytes=$file.Length }
        Remove-Item -LiteralPath $candidate
        break
    }
}
@{source_base=(git rev-parse HEAD); reason='Retain build headroom by removing only identical committed source archive copies'; copies=$records; reclaimed_bytes=($records | Measure-Object -Property bytes -Sum).Sum} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'out/campaign/editor-prior-reclamation.json' -Encoding utf8
Write-Output "Reclaimed $($records.Count) verified archive duplicates."
