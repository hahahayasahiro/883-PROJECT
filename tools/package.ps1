$ErrorActionPreference = 'Stop'
$source = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$destination = Join-Path (Split-Path $source -Parent) 'SmartCampus-enhanced-delivery.zip'
if (Test-Path -LiteralPath $destination) { throw 'Delivery archive already exists. Choose a new name rather than overwriting it.' }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::Open($destination, [IO.Compression.ZipArchiveMode]::Create)
try {
  $files = Get-ChildItem -LiteralPath $source -File -Recurse -Force | Where-Object {
    $relative = $_.FullName.Substring($source.Length + 1)
    $relative -notmatch '^(\.venv|\.build|\.pytest_cache|\.git|node_modules|data|deliverables\\video[^\\]*)(\\|$)' -and
    $relative -notmatch '(^|\\)__pycache__(\\|$)' -and
    $relative -ne '.env'
  }
  foreach ($file in $files) {
    $entry = 'smartcampus/' + $file.FullName.Substring($source.Length + 1).Replace('\','/')
    [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $file.FullName, $entry, [IO.Compression.CompressionLevel]::Optimal) | Out-Null
  }
} finally { $archive.Dispose() }
Write-Output $destination
