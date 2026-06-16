# make_submission.ps1
# Teslim paketini olusturur: 2022280084_ozgurdalbeler_final.zip
#
# Zip'in KOKUNE su ogeleri koyar (sarmalayici klasor olmadan, ZIP standardi ileri-slash ile):
#   src/  tests/  inputs/  report.md  README.md  debugging_logs/
# Diger her sey (docs/, FINAL_QUESTION.md, CLAUDE.md, exam_answers.md,
# requirements.txt, make_submission.ps1, .venv, .idea ...) teslime GIRMEZ.
# __pycache__/.pytest_cache/*.pyc temizlenir. Bos debugging_logs/ klasoru korunur.
#
# Calistirmak icin (repo kokunden):
#   powershell -ExecutionPolicy Bypass -File .\make_submission.ps1

$ErrorActionPreference = 'Stop'
$root    = $PSScriptRoot
$zipName = '2022280084_ozgurdalbeler_final.zip'
$zipPath = Join-Path $root $zipName

# Zip kokune girecek teslim ogeleri
$include = @('src', 'tests', 'inputs', 'report.md', 'README.md', 'debugging_logs')

$missing = $include | Where-Object { -not (Test-Path (Join-Path $root $_)) }
if ($missing) { throw ("Eksik teslim ogesi: " + ($missing -join ', ')) }

# Temiz staging klasoru (cache/pyc'yi disarida birakmak icin)
$stage = Join-Path $env:TEMP 'final_submission_stage'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

Add-Type -AssemblyName System.IO.Compression | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null

try {
    foreach ($item in $include) {
        Copy-Item -Path (Join-Path $root $item) -Destination $stage -Recurse -Force
    }

    # Cache/pyc temizligi
    Get-ChildItem $stage -Recurse -Force -Directory |
        Where-Object { $_.Name -in '__pycache__', '.pytest_cache' } |
        Remove-Item -Recurse -Force
    Get-ChildItem $stage -Recurse -Force -Filter *.pyc | Remove-Item -Force

    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

    # Staging kok yolu (rel yol hesabi icin)
    $prefix = [System.IO.Path]::GetFullPath($stage)
    if (-not $prefix.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $prefix += [System.IO.Path]::DirectorySeparatorChar
    }

    # Zip'i ELLE, ileri-slash girdilerle olustur (tasinabilirlik icin)
    $fs = [System.IO.File]::Open($zipPath, [System.IO.FileMode]::Create)
    $archive = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($f in Get-ChildItem $stage -Recurse -File) {
            $rel = $f.FullName.Substring($prefix.Length).Replace('\', '/')
            $entry = $archive.CreateEntry($rel, [System.IO.Compression.CompressionLevel]::Optimal)
            $in  = [System.IO.File]::OpenRead($f.FullName)
            $out = $entry.Open()
            $in.CopyTo($out)
            $out.Dispose(); $in.Dispose()
        }
        # Bos klasorler (orn. debugging_logs/) explicit entry olarak
        foreach ($d in Get-ChildItem $stage -Recurse -Directory) {
            $hasFile = Get-ChildItem $d.FullName -Recurse -File | Select-Object -First 1
            if (-not $hasFile) {
                $rel = $d.FullName.Substring($prefix.Length).Replace('\', '/').TrimEnd('/') + '/'
                $archive.CreateEntry($rel) | Out-Null
            }
        }
    }
    finally {
        $archive.Dispose(); $fs.Dispose()
    }

    Write-Host ("Olusturuldu: " + $zipPath)
    Write-Host "--- Zip icerigi ---"
    $zr = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    $zr.Entries | ForEach-Object { Write-Host ("  " + $_.FullName) }
    $zr.Dispose()
}
finally {
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
}
