# aec-harness

Mimarlık ofisi için Claude Code eklentisi (plugin marketplace). Hedef: ajan çizimdeki ölçüleri görselden tahmin
etmesin, araçla okusun; Revit'e onaylı bir plan üzerinden yazsın, yazdıktan sonra Revit'ten geri okuyup sonucu
toleransla doğrulasın. Bugün bunun ilk katmanı çalışıyor (plan, onay ve ofis kuralları); ölçüyü okuyan ve geri okumayı
doğrulayan araçlar yakında. Ayrıntı aşağıdaki "Durum" bölümünde.

## Durum

Bugün çalışanlar: karşılama kapısı (isteğinizi tanıyıp önce plan gösterir), ofis kuralları ve üç komut
(`/aec:kontrol-et`, `/aec:proje-baslat`, `/aec:yardim`). Program bağlantıları (DWG okuma, Revit köprüsü,
AutoCAD, Rhino) ve modüller (asma tavan, metraj, render) yakında. Ayrıntı:
[Neler yapabilir?](plugin/docs/NELER-YAPABILIR.md)

## Kurulum

Adım adım kurulum (terminal ve Cowork için): [plugin/docs/BASLA.md](plugin/docs/BASLA.md). Güvenlik kuralları:
[GUVENLIK.md](plugin/docs/GUVENLIK.md). Takılırsanız: [SORUN-GIDERME.md](plugin/docs/SORUN-GIDERME.md).

### Elle kurulum (yalnızca BT/şampiyon için)

`C:\Users\<kullanıcı>\.claude\settings.json` dosyasına şunu ekleyin. Dosyada başka ayarlar varsa bu anahtarları
onların yanına koyun. Claude Code bir sonraki açılışta eklentiyi kendisi indirip kurar ve güncel tutar. uv'yi
ayrıca kurun (`winget install --id=astral-sh.uv -e`).

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

Otomatik güncelleme kapalı görünürse: `/plugin` > Marketplaces > aec-office > Enable auto-update.

## Kanallar

- `main`: herkes için kararlı kanal. Korumalıdır, yalnızca PR ile değişir.
- `dev`: şampiyonlar için deneme kanalı. Kurulum: [BASLA.md, Kanallar bölümü](plugin/docs/BASLA.md).

Şampiyon iki kanalı aynı anda kuramaz, çünkü marketplace adı aynıdır.

## Rol ve ofis kuralları

Eklenti her oturumun başında iki dosyayı Claude'un bağlamına ekler:

- `plugin/standards/rol.md`: ajanın rolü ve çalışma biçimi (30 yıllık mimar). Revit, AutoCAD ya da Rhino'ya yalnızca
  o programın MCP aracı oturumda varsa bağlanır; yoksa bağlantının kurulu olmadığını söyler ve `/aec:kontrol-et` önerir.
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

İşler `dev` dalında yapılır. Pilotta denenip oturan değişiklik PR ile `main`'e geçer. `main` dalına yapılan her push,
bir sonraki açılışta bütün üyelere ulaşır. Bu yüzden `main` korumalıdır: PR açılır ve CI'daki `test` kontrolü yeşil
olmadan birleştirilmez. Değişiklikler [CHANGELOG.md](CHANGELOG.md) dosyasına yazılır.

Koruma repo ayarlarından bir kez kurulur (Settings → Branches → *Add classic branch protection rule*):

- *Branch name pattern*: `main`
- **Require a pull request before merging** işaretli. Altında kendiliğinden işaretlenen **Require approvals**
  kaldırılır. Repoyu tek kişi yönettiği sürece bu kutu açık kalırsa her birleştirmede korumayı atlamak gerekir, çünkü
  GitHub kişinin kendi PR'ını onaylamasına izin vermez. İkinci bir bakımcı gelince açılır.
- **Require status checks to pass before merging** işaretli, listeden `test` seçili.
- **Create** ile kaydedilir.

## Lisans

MIT. Ayrıntı için [LICENSE](LICENSE) dosyasına bakın. Telif hakkı © 2026 BelenPartners.
