$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$inputFile = Join-Path $root 'deliverables\SmartCampus_中英文对照使用说明书.docx'
$renderFolder = Join-Path $root '.build\manual-render'
New-Item -ItemType Directory -Path $renderFolder -Force | Out-Null
$pdf = Join-Path $renderFolder 'manual-preview.pdf'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($inputFile, $false, $false, $false)
    $document.Repaginate()
    $document.Fields.Update() | Out-Null
    $document.Repaginate()
    $document.Fields.Update() | Out-Null
    $pages = $document.ComputeStatistics(2)
    $document.Save()
    $document.ExportAsFixedFormat($pdf, 17)
    Write-Output ('Manual rendered using native Word. Pages: ' + $pages)
} finally {
    if ($null -ne $document) { try { $document.Close(0) | Out-Null } catch {}; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document) }
    if ($null -ne $word) { try { $word.Quit() | Out-Null } catch {}; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
