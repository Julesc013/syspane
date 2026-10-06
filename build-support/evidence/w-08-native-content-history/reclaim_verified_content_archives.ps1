$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath '.').ProviderPath
if ($taskRoot -ne 'D:\Projects\SysPane\syspane') { throw 'Unexpected workspace' }
$outputRoot = (Resolve-Path -LiteralPath (Join-Path $taskRoot 'out\campaign')).ProviderPath
$groups = @(
    @('w-08-content-resolution', 'w-08-content-history'),
    @('w-08-resource-generations', 'w-08-resources-history'),
    @('w-08-supervised-transactions', 'w-08-supervision-history')
)
$targets = @(); $records = @(); [long]$totalBytes = 0
foreach ($group in $groups) {
    $target = (Resolve-Path -LiteralPath (Join-Path $outputRoot $group[0])).ProviderPath
    if (-not $target.StartsWith($outputRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target escapes output root' }
    $nodes = @(Get-Item -LiteralPath $target) + @(Get-ChildItem -LiteralPath $target -Recurse -Force)
    if ($nodes | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw 'Reparse point in cached archive' }
    foreach ($attempt in Get-ChildItem -LiteralPath $target -Force) {
        if (-not $attempt.PSIsContainer -or $attempt.Name -notmatch '^(linux-x64-gcc13|windows-x64-gcc15|windows-x86-v141-xp)-(configure|build|focus|oracle|test)-[0-9a-f]{10}$') { throw 'Unexpected attempt entry' }
        $files = @(Get-ChildItem -LiteralPath $attempt.FullName -Force)
        if ($files.Count -ne 2) { throw 'Unexpected attempt contents' }
        foreach ($file in $files) {
            if ($file.PSIsContainer -or $file.Name -notin @('result.json', 'source-inputs.zip')) { throw 'Unexpected cached file' }
            $relative = 'build-support/evidence/' + $group[1] + '/' + $attempt.Name + '/' + $file.Name
            $preserved = Join-Path $taskRoot $relative
            & git ls-files --error-unmatch -- $relative > $null
            if ($LASTEXITCODE -ne 0) { throw 'Evidence is not tracked' }
            & git diff --quiet HEAD -- $relative
            if ($LASTEXITCODE -ne 0) { throw 'Evidence differs from committed state' }
            $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($digest -ne (Get-FileHash -LiteralPath $preserved -Algorithm SHA256).Hash.ToLowerInvariant()) { throw 'Preserved evidence differs' }
            $records += @{ cached = $file.FullName; preserved = $relative; sha256 = $digest; bytes = $file.Length }
            $totalBytes += $file.Length
        }
    }
    $targets += $target
}
$auditPath = Join-Path $outputRoot 'native-content-cache-reclamation.json'
$audit = @{ outcome = 'verified'; source_base = (& git rev-parse HEAD); targets = $targets; bytes = $totalBytes; files = $records }
$audit | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $auditPath -Encoding utf8NoBOM
foreach ($target in $targets) {
    $resolved = (Resolve-Path -LiteralPath $target).ProviderPath
    if ($resolved -ne $target -or -not $resolved.StartsWith($outputRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target changed before deletion' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
$audit.outcome = 'reclaimed_verified_duplicates'
$audit | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $auditPath -Encoding utf8NoBOM
Write-Output "Reclaimed $totalBytes bytes from $($targets.Count) owned cache directories; all $($records.Count) files remain byte-identical in committed evidence."
