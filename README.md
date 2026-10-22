# aec-harness

Mimarlık ofisi için Claude Code eklentisi (plugin marketplace). Ajan çizimdeki ölçüleri görselden tahmin etmez,
araçla okur. Revit'e bir plan üzerinden yazar, yazdıktan sonra Revit'ten geri okur ve sonucu toleransla doğrular.

Durum: Faz 1A (temel). DWG okuma, Revit köprüsü ve tavan modülü sonraki aşamalarda gelecek.

## Üye kurulumu

Claude Code'a şunu yazmanız yeterli:

> https://github.com/modularbelen-del/aec-harness bunu ekle

Claude Code bu bölümü okuyup aşağıdaki adımları uygular; izin isterse onaylayın. Kurulum kullanıcı düzeyindedir:
bu oturuma özel değildir, bütün projelerde ve bütün oturumlarda çalışır.

1. Eklentiyi kurar: `claude plugin install aec --marketplace modularbelen-del/aec-harness`
2. Otomatik güncellemeyi açar: `~/.claude/settings.json` içinde `extraKnownMarketplaces` → `aec-office` altına
   `"autoUpdate": true` ekler. Dosyadaki diğer ayarlara dokunmaz.
3. `uv --version` ile [uv](https://docs.astral.sh/uv/)'yi kontrol eder. Kurulu değilse
   `winget install --id=astral-sh.uv -e` ile kurar.
4. Claude Code'u kapatıp yeniden açmanızı ister.

### Elle kurulum

`C:\Users\<kullanıcı>\.claude\settings.json` dosyasına şunu ekleyin. Dosyada başka ayarlar varsa bu anahtarları
onların yanına koyun. Claude Code bir sonraki açılışta eklentiyi kendisi indirip kurar ve güncel tutar. uv'yi
yukarıdaki 3. adımdaki gibi ayrıca kurun.

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

### Kontrol

Claude Code'u yeniden açın ve `/plugin` yazın. `aec` kurulu görünmeli, `aec-office` marketplace'inde de
otomatik güncelleme açık olmalı. Sonra yeni bir oturumda "Ofisin yetki sırası ne?" diye sorun. Cevap şu sırayı
vermeli: çizim, proje kuralları, ofis standartları, araştırma kataloğu. Kurulu görünmüyorsa terminalde
`claude plugin install aec@aec-office` çalıştırın. Otomatik güncelleme kapalıysa `/plugin` → Marketplaces →
`aec-office` → Enable auto-update yolundan açın.

Revit, AutoCAD ve Rhino tarafındaki kurulum ilerideki aşamalarda `kur.ps1` ile gelecek.

## Rol ve ofis kuralları

Eklenti her oturumun başında iki dosyayı Claude'un bağlamına ekler:

- `plugin/standards/rol.md`: ajanın rolü ve çalışma biçimi (30 yıllık mimar, Revit/AutoCAD/Rhino'ya MCP ile bağlanır).
- `plugin/standards/authority.md`: çelişkide hangi kaynağın kazandığı (yetki sırası).

Bunları değiştirmek için PR açın. Birleştirilince bütün üyelere bir sonraki açılışta ulaşır.

## Bakımcı komutları

```powershell
uv sync --project plugin                 # ortamı kur
uv run --project plugin pytest -q        # testler
claude plugin validate .                 # marketplace manifesti
claude plugin validate plugin            # plugin manifesti
```

## Değişiklik akışı

`main` dalına yapılan her push, bir sonraki açılışta bütün üyelere ulaşır. Bu yüzden `main` korumalıdır: değişiklik
ayrı bir dalda hazırlanır, PR açılır ve CI'daki `test` kontrolü yeşil olmadan birleştirilmez.

Koruma repo ayarlarından bir kez kurulur (Settings → Branches → *Add classic branch protection rule*):

- *Branch name pattern*: `main`
- **Require a pull request before merging** işaretli. Altında kendiliğinden işaretlenen **Require approvals**
  kaldırılır. Repoyu tek kişi yönettiği sürece bu kutu açık kalırsa her birleştirmede korumayı atlamak gerekir, çünkü
  GitHub kişinin kendi PR'ını onaylamasına izin vermez. İkinci bir bakımcı gelince açılır.
- **Require status checks to pass before merging** işaretli, listeden `test` seçili.
- **Create** ile kaydedilir.

## Lisans

MIT. Ayrıntı için [LICENSE](LICENSE) dosyasına bakın. Telif hakkı © 2026 BelenPartners.
