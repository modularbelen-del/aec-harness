# aec-harness

Mimarlık ofisi için Claude Code eklentisi (plugin marketplace). Ajan çizimdeki ölçüleri görselden tahmin etmez,
araçla okur. Revit'e bir plan üzerinden yazar, yazdıktan sonra Revit'ten geri okur ve sonucu toleransla doğrular.

Durum: Faz 1A (temel). DWG okuma, Revit köprüsü ve tavan modülü sonraki aşamalarda gelecek.

## Üye kurulumu

`C:\Users\<kullanıcı>\.claude\settings.json` dosyasına şunu ekleyin. Dosyada başka ayarlar varsa bu anahtarları
onların yanına koyun. Claude Code bir sonraki açılışta eklentiyi kendisi indirip kurar ve güncel tutar.

```json
{
  "extraKnownMarketplaces": {
    "aec-office": {
      "source": { "source": "github", "repo": "modularbelen-del/aec-harness" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "aec@aec-office": true
  }
}
```

Kontrol: Claude Code'u yeniden açın ve `/plugin` yazın. `aec` kurulu görünmeli, `aec-office` marketplace'inde de
otomatik güncelleme açık olmalı. Kurulu görünmüyorsa terminalde `claude plugin install aec@aec-office`
çalıştırın. Otomatik güncelleme kapalıysa `/plugin` → Marketplaces → `aec-office` → Enable auto-update yolundan açın.

Gereken program: [uv](https://docs.astral.sh/uv/). Revit, AutoCAD ve Rhino tarafındaki kurulum ilerideki
aşamalarda `kur.ps1` ile gelecek.

## Bakımcı komutları

```powershell
uv sync --project plugin                 # ortamı kur
uv run --project plugin pytest -q        # testler
claude plugin validate .                 # marketplace manifesti
claude plugin validate plugin            # plugin manifesti
```

`main` dalına yapılan her push, bir sonraki açılışta bütün üyelere ulaşır. Değişiklikler PR ile girer ve CI yeşil
olmadan birleştirilmez.

## Lisans

MIT. Ayrıntı için [LICENSE](LICENSE) dosyasına bakın. Telif hakkı © 2026 BelenPartners.
