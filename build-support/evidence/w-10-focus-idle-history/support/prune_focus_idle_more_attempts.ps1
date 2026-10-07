$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath('D:\Projects\SysPane\syspane\out\campaign')
$taskPlan = Get-Content -LiteralPath (Join-Path $taskRoot 'focus-idle-more-prune-plan.json') -Raw | ConvertFrom-Json
foreach ($entry in $taskPlan.entries) {
    $target = [IO.Path]::GetFullPath($entry.path)
    if (-not ($target.StartsWith((Join-Path $taskRoot 'w-10-snap') + '\') -or $target.StartsWith((Join-Path $taskRoot 'w-10-arrange') + '\'))) { throw 'Unexpected cleanup target' }
    $rootItem = Get-Item -LiteralPath $target
    if ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked cleanup target' }
    $items = @(Get-ChildItem -LiteralPath $target -Force)
    $expected = @($entry.files.PSObject.Properties)
    if ($items.Count -ne $expected.Count) { throw 'Unrecorded cleanup content' }
    foreach ($item in $items) {
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Unexpected nested cleanup content' }
        $digest = $entry.files.PSObject.Properties[$item.Name].Value
        if (-not $digest -or (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $digest) { throw 'Changed cleanup content' }
    }
}
foreach ($entry in $taskPlan.entries) { Remove-Item -LiteralPath $entry.path -Recurse -Force }
$taskPlan | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $taskRoot 'focus-idle-more-pruned-attempts.json') -Encoding utf8
'Removed verified committed attempt duplicates.'
