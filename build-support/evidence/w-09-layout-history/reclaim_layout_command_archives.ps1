$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath '.').ProviderPath
if ($taskRoot -ne 'D:\Projects\SysPane\syspane') { throw 'Unexpected workspace' }
$outputRoot = (Resolve-Path -LiteralPath (Join-Path $taskRoot 'out\campaign')).ProviderPath
$cacheRoot = (Resolve-Path -LiteralPath (Join-Path $outputRoot 'w-08-command')).ProviderPath
if ($cacheRoot -ne (Join-Path $outputRoot 'w-08-command')) { throw 'Unexpected cache root' }
$nodes = @(Get-Item -LiteralPath $cacheRoot) + @(Get-ChildItem -LiteralPath $cacheRoot -Recurse -Force)
if ($nodes | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw 'Reparse point in cache' }
$targets = @(); $records = @(); $retained = @(); [long]$totalBytes = 0
foreach ($attempt in Get-ChildItem -LiteralPath $cacheRoot -Force) {
    if (-not $attempt.PSIsContainer -or $attempt.Name -notmatch '^(linux-x64-gcc13|windows-x64-gcc15|windows-x86-v141-xp)-(configure|build|focus|oracle|test)-[0-9a-f]{10}$') { throw 'Unexpected attempt entry' }
    $files = @(Get-ChildItem -LiteralPath $attempt.FullName -Force)
    if ($files.Count -eq 0) { $retained += $attempt.FullName; continue }
    if ($files.Count -ne 2) { throw 'Unexpected attempt contents' }
    foreach ($file in $files) {
        if ($file.PSIsContainer -or $file.Name -notin @('result.json','source-inputs.zip')) { throw 'Unexpected cached file' }
        $relative = 'build-support/evidence/w-08-command-history/' + $attempt.Name + '/' + $file.Name
        & git ls-files --error-unmatch -- $relative > $null
        if ($LASTEXITCODE -ne 0) { throw 'Evidence not tracked' }
        & git diff --quiet HEAD -- $relative
        if ($LASTEXITCODE -ne 0) { throw 'Evidence changed from committed state' }
        $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($digest -ne (Get-FileHash -LiteralPath (Join-Path $taskRoot $relative) -Algorithm SHA256).Hash.ToLowerInvariant()) { throw 'Preserved evidence differs' }
        $records += @{ cached=$file.FullName; preserved=$relative; sha256=$digest; bytes=$file.Length }
        $totalBytes += $file.Length
    }
    $targets += $attempt.FullName
}
$auditPath = Join-Path $outputRoot 'layout-command-cache-reclamation.json'
$audit = @{ outcome='verified'; source_base=(& git rev-parse HEAD); targets=$targets; bytes=$totalBytes; files=$records; retained_empty_attempts=$retained }
$audit | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $auditPath -Encoding utf8NoBOM
foreach ($target in $targets) {
    $resolved = (Resolve-Path -LiteralPath $target).ProviderPath
    if ($resolved -ne $target -or -not $resolved.StartsWith($cacheRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target changed or escapes cache root' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
$audit.outcome='reclaimed_verified_duplicates'
$audit | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $auditPath -Encoding utf8NoBOM
Write-Output "Reclaimed $totalBytes bytes from $($targets.Count) completed attempts; $($retained.Count) empty attempts retained."
