# AEC ofis kurulumu. Bir kez çalıştırılır.
# Normal kurulum (kararlı kanal):
#   powershell -ExecutionPolicy Bypass -c "iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
# Deneme (dev) kanalı, şampiyon için (Win+R ya da cmd penceresine yazın; PowerShell penceresinde $env: önce açılır):
#   powershell -ExecutionPolicy Bypass -c "$env:AEC_KANAL='dev'; iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
# (TrimStart, dosyanın başındaki BOM işaretini ayıklar; olmazsa iex ilk satırda hata verir.)
# Yalnızca ne yapacağını görmek için (hiçbir şey kurmaz): -KuruCalistir ya da $env:AEC_KURU='1'
param(
    [ValidateSet('stable', 'dev')]
    [string]$Kanal = 'stable',
    [switch]$KuruCalistir
)

# irm | iex yolunda parametre verilemez; ortam değişkenleri yedek olarak okunur.
if (-not $PSBoundParameters.ContainsKey('Kanal') -and $env:AEC_KANAL -in @('stable', 'dev')) {
    $Kanal = $env:AEC_KANAL
}
$Kuru = [bool]$KuruCalistir -or ($env:AEC_KURU -eq '1')

[Console]::OutputEncoding = [Text.Encoding]::UTF8
$ErrorActionPreference = 'Continue'

$Kaynak = 'modularbelen-del/aec-harness'
if ($Kanal -eq 'dev') { $Kaynak = 'modularbelen-del/aec-harness#dev' }

function Komut-Var([string]$ad) {
    return [bool](Get-Command $ad -ErrorAction SilentlyContinue)
}

function Yaz-Adim([int]$n, [string]$metin) {
    Write-Output ''
    Write-Output "[$n/5] $metin"
}

function Yaz-Not([string]$metin) {
    Write-Output "      $metin"
}

function Set-AecOtomatikGuncelleme {
    param([string]$Yol, [string]$Kanal)
    $kaynak = [ordered]@{ source = 'github'; repo = 'modularbelen-del/aec-harness' }
    if ($Kanal -eq 'dev') { $kaynak['ref'] = 'dev' }
    $yedekMetni = ''
    try {
        $ayar = $null
        if (Test-Path -LiteralPath $Yol) {
            $ham = [IO.File]::ReadAllText($Yol, (New-Object Text.UTF8Encoding($false)))
            if ($ham -and $ham.Trim()) {
                try { $ayar = $ham | ConvertFrom-Json -ErrorAction Stop }
                catch { return 'Ayar dosyanız (settings.json) okunamadı, bu yüzden dokunulmadı. Dosyayı şampiyona gösterin.' }
                if ($ayar -isnot [pscustomobject]) {
                    return 'Ayar dosyanız (settings.json) beklenen biçimde değil, bu yüzden dokunulmadı. Dosyayı şampiyona gösterin.'
                }
                $yedek = $Yol + '.aec-yedek'
                if (-not (Test-Path -LiteralPath $yedek)) {
                    Copy-Item -LiteralPath $Yol -Destination $yedek
                    $yedekMetni = ' Eski ayarlar settings.json.aec-yedek olarak saklandı.'
                }
            }
        } else {
            New-Item -ItemType Directory -Force -Path (Split-Path $Yol) | Out-Null
        }
        if ($null -eq $ayar) { $ayar = [pscustomobject]@{} }
        if (-not $ayar.PSObject.Properties['extraKnownMarketplaces']) {
            $ayar | Add-Member -NotePropertyName extraKnownMarketplaces -NotePropertyValue ([pscustomobject]@{})
        }
        $mp = $ayar.extraKnownMarketplaces
        if (-not $mp.PSObject.Properties['aec-office']) {
            $mp | Add-Member -NotePropertyName 'aec-office' -NotePropertyValue ([pscustomobject]@{})
        }
        $ofis = $mp.'aec-office'
        $yeniKaynak = [pscustomobject]$kaynak
        $mevcut = $null
        if ($ofis.PSObject.Properties['source']) { $mevcut = $ofis.source }
        $ayniKanal = $false
        if ($null -ne $mevcut -and $mevcut -is [pscustomobject]) {
            $mevcutRef = $null
            if ($mevcut.PSObject.Properties['ref']) { $mevcutRef = $mevcut.ref }
            $istenenRef = $null
            if ($Kanal -eq 'dev') { $istenenRef = 'dev' }
            $ayniKanal = ($mevcutRef -eq $istenenRef)
        }
        if (-not $ayniKanal) {
            if ($ofis.PSObject.Properties['source']) { $ofis.source = $yeniKaynak }
            else { $ofis | Add-Member -NotePropertyName source -NotePropertyValue $yeniKaynak }
        }
        if ($ofis.PSObject.Properties['autoUpdate']) { $ofis.autoUpdate = $true }
        else { $ofis | Add-Member -NotePropertyName autoUpdate -NotePropertyValue $true }
        $json = $ayar | ConvertTo-Json -Depth 32
        [IO.File]::WriteAllText($Yol, $json, (New-Object Text.UTF8Encoding($false)))
        return ('Otomatik güncelleme açıldı.' + $yedekMetni)
    } catch {
        return 'Otomatik güncelleme açılamadı. Eklenti yine de çalışır; şampiyona haber verin.'
    }
}

# Testler için: yalnızca işlevleri tanımla, adımları çalıştırma.
if ($env:AEC_SADECE_YUKLE -eq '1') { return }
if ($Kuru) {
    Write-Output '(kuru) Bu bir deneme çalıştırmasıdır. Hiçbir şey kurulmaz ya da değiştirilmez.'
}
Write-Output "Kanal: $Kanal  |  Kaynak: $Kaynak"

# --- 1/5 uv ---
Yaz-Adim 1 'uv aracı kontrol ediliyor (Python işlerini çalıştırır).'
if (Komut-Var 'uv') {
    Yaz-Not 'uv zaten kurulu.'
} elseif ($Kuru) {
    if (Komut-Var 'winget') {
        Yaz-Not '(kuru) uv kurulacak: winget install --id=astral-sh.uv -e'
    } else {
        Yaz-Not '(kuru) winget yok; uv şu adresten kurulacak: https://astral.sh/uv/install.ps1'
    }
} else {
    try {
        if (Komut-Var 'winget') {
            Yaz-Not 'uv kuruluyor (winget)...'
            winget install --id=astral-sh.uv -e --accept-source-agreements --accept-package-agreements
        } else {
            Yaz-Not 'uv kuruluyor (astral.sh)...'
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        }
        # Yeni kurulan uv bu pencerede bulunsun diye yolu yenile.
        $env:Path = $env:Path + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + (Join-Path $env:USERPROFILE '.local\bin')
        if (Komut-Var 'uv') { Yaz-Not 'uv kuruldu.' }
        else { Yaz-Not 'uv kurulamadı. Bu pencereyi kapatıp yeniden deneyin; olmazsa şampiyona haber verin.' }
    } catch {
        Yaz-Not 'uv kurulurken bir sorun çıktı. Şampiyona haber verin.'
    }
}

# --- 2/5 Python ---
Yaz-Adim 2 'Python 3.12 hazırlanıyor (ilk kullanımda beklememek için).'
if ($Kuru) {
    Yaz-Not '(kuru) çalıştırılacak: uv python install 3.12'
} elseif (Komut-Var 'uv') {
    try {
        uv python install 3.12
        if ($LASTEXITCODE -eq 0) { Yaz-Not 'Python 3.12 hazır.' }
        else { Yaz-Not 'Python 3.12 hazırlanamadı. Şampiyona haber verin.' }
    } catch {
        Yaz-Not 'Python 3.12 hazırlanırken bir sorun çıktı. Şampiyona haber verin.'
    }
} else {
    Yaz-Not 'uv bulunamadığı için Python adımı atlandı.'
}

# --- 3/5 ve 4/5 Eklenti ---
if (Komut-Var 'claude') {
    Yaz-Adim 3 'Claude Code için AEC eklentisi kuruluyor ve otomatik güncelleme açılıyor.'
    if ($Kuru) {
        Yaz-Not "(kuru) çalıştırılacak: claude plugin marketplace add $Kaynak"
        Yaz-Not '(kuru) çalıştırılacak: claude plugin install aec@aec-office'
        Yaz-Not '(kuru) önce ~/.claude/settings.json yedeklenecek (settings.json.aec-yedek), sonra yalnızca extraKnownMarketplaces.aec-office.autoUpdate = true yazılacak.'
    } else {
        $eklendi = $false
        try {
            $cikti = & claude plugin marketplace add $Kaynak 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0 -or $cikti -match 'already') {
                $eklendi = $true
                Yaz-Not 'Eklenti kaynağı eklendi (ya da zaten vardı).'
            } else { Yaz-Not 'Eklenti kaynağı eklenemedi. Şampiyona haber verin.' }
            if ($eklendi) {
                $cikti = & claude plugin install aec@aec-office 2>&1 | Out-String
                if ($LASTEXITCODE -eq 0 -or $cikti -match 'already') { Yaz-Not 'AEC eklentisi kuruldu (ya da zaten vardı).' }
                else { Yaz-Not 'AEC eklentisi kurulamadı. Şampiyona haber verin.' }
            }
        } catch {
            Yaz-Not 'Eklenti kurulurken bir sorun çıktı. Şampiyona haber verin.'
        }

        # Otomatik güncelleme için CLI bayrağı yok; ayar dosyasına yalnızca tek kayıt yazılır.
        if ($eklendi) {
            Yaz-Not (Set-AecOtomatikGuncelleme -Yol (Join-Path $env:USERPROFILE '.claude\settings.json') -Kanal $Kanal)
        } else {
            Yaz-Not 'Eklenti kaynağı eklenemediği için otomatik güncelleme ayarına dokunulmadı.'
        }    }
    Yaz-Adim 4 'Claude Code bulundu; bu adım gerekmiyor.'
} else {
    Yaz-Adim 3 'Claude Code (terminal) bulunamadı; eklenti burada kurulmayacak.'
    Yaz-Adim 4 "Cowork kullanıyorsanız BASLA.md'deki ekran adımlarına geçin."
}

# --- 5/5 Revit ---
Yaz-Adim 5 'Revit tarafı kontrol ediliyor (yalnızca bilgi verilir, bir şey kurulmaz).'
if (Komut-Var 'pyrevit') { Yaz-Not 'pyRevit bulundu.' } else { Yaz-Not 'pyRevit bulunamadı.' }
$uzanti = Join-Path $env:APPDATA 'pyRevit\Extensions\mcp-server-for-revit-python.extension'
if (Test-Path -LiteralPath $uzanti) { Yaz-Not 'Revit bağlantı eklentisi bulundu.' } else { Yaz-Not 'Revit bağlantı eklentisi bulunamadı (sonraki sürümde kurulacak).' }

Write-Output ''
if ($Kuru) { Write-Output '(kuru) Deneme bitti. Hiçbir şey değiştirilmedi.' }
Write-Output "Claude'u yeniden açın ve /aec:kontrol-et yazın."
if (-not $Kuru) { Read-Host 'Kapatmak için Enter''a basın' }
