$ErrorActionPreference = 'Stop'
$repoRoot = (Get-Location).Path
if ($repoRoot -ne 'D:\Projects\SysPane\syspane') { throw 'Unexpected checkout' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'out/campaign/w-09-image-pipeline'))
$records = @()
$paths = git ls-files 'build-support/evidence/w-09-image-pipeline-history/*/source-inputs.zip'
foreach ($relative in $paths) {
    $archive = (Resolve-Path -LiteralPath (Join-Path $repoRoot $relative)).Path
    $attemptName = [IO.Path]::GetFileName([IO.Path]::GetDirectoryName($archive))
    $candidate = [IO.Path]::GetFullPath((Join-Path $sourceRoot "$attemptName/source-inputs.zip"))
    if (-not $candidate.StartsWith($sourceRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside owned output' }
    if (-not (Test-Path -LiteralPath $candidate)) { continue }
    $resolved = (Resolve-Path -LiteralPath $candidate).Path
    if ($resolved -ne $candidate) { throw 'Unexpected resolved path' }
    $expected = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash -ne $expected) { throw 'Archive bytes differ' }
    git diff --quiet HEAD -- $relative
    if ($LASTEXITCODE -ne 0) { throw 'Archive is not unchanged committed evidence' }
    $records += @{ removed=$resolved; retained=$relative; sha256=$expected.ToLowerInvariant(); bytes=(Get-Item -LiteralPath $resolved).Length }
    Remove-Item -LiteralPath $resolved
}
@{ source_base=(git rev-parse HEAD); reason='Reclaim verified committed duplicate inputs before the next admitted native scene build'; copies=$records; reclaimed_bytes=($records | Measure-Object -Property bytes -Sum).Sum } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'out/campaign/scene-images-input-reclamation.json' -Encoding utf8
Write-Output "Reclaimed $($records.Count) verified committed archive copies."
