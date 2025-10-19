# Usage: pwsh ./scripts/compile_translations.ps1

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$bin = Join-Path $root 'gettext0.26-iconv1.17-static-64\bin'

if (-not (Test-Path $bin)) {
  Write-Error "Gettext bin not found at $bin"
}

$msgfmt = Join-Path $bin 'msgfmt.exe'

Get-ChildItem -Path (Join-Path $root 'locale') -Recurse -Filter 'django.po' | ForEach-Object {
  $po = $_.FullName
  $mo = [System.IO.Path]::ChangeExtension($po, '.mo')
  Write-Host "Compiling" $po '->' $mo
  & $msgfmt -o $mo $po
}

Write-Host 'Done.'

