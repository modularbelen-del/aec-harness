# aec-harness

Mimarlık ofisleri için geliştirilmiş bir Claude eklentisidir (Claude Code plugin marketplace: `aec-office`, eklenti:
`aec`). Revit, AutoCAD ve Rhino ile yürütülen günlük işler için hazırlanmıştır. İstekler gündelik dille yazılabilir;
eklenti işi tanır, eksik bilgileri sorar ve uygulamadan önce planı onaya sunar.

Hedef, ajanın ölçüleri görselden tahmin etmek yerine araçla okuması, Revit'e yalnızca onaylanmış bir plan üzerinden
ve kopya dosyada yazması, yazdıktan sonra da sonucu Revit'ten okuyarak toleransla karşılaştırmasıdır. Öngörülen iş
akışı: **ölç → planla → onayla → uygula → geri oku → doğrula**.

Bu akışın ilk katmanı kullanımdadır: isteği tanıyarak önce plan sunan **istek karşılama katmanı (ön kapı)**, ofis
kuralları ve üç komut. Ölçü okuyan ve geri okumayı doğrulayan araçlar sonraki fazlarda eklenecektir. Kullanımdaki ve
planlanan bileşenler aşağıda ayrı ayrı belirtilmiştir.

## Durum

| Bileşen | Durum |
|---|---|
| İstek karşılama katmanı (isteği tanır, eksikleri sorar, plan sunar, onay bekler) | Kullanımda; `dev` kanalında, pilot aşamasında |
| Ofis kuralları ve rol tanımı (her oturumun başında yüklenir) | Kullanımda |
| `/aec:kontrol-et`, `/aec:proje-baslat`, `/aec:yardim` | Kullanımda; `dev` kanalında |
| Tek satırlık kurulum (`kur.ps1`) | Kullanımda; `dev` kanalında |
| Revit bağlantısı | Ofis tarafından kurulum yapılmış bilgisayarlarda temel bağlantı mevcuttur; kurulumla dağıtımı bir sonraki planda yer almaktadır |
| AutoCAD ve Rhino bağlantısı | Yakında (bir sonraki plan) |
| .NET 8, .NET 10, pyRevit kurulumu | Yakında (bir sonraki plan) |
| DWG okuma (Faz 1B), doğrulayan Revit köprüsü (Faz 1C), asma tavan (Faz 1D) | Yakında |
| Metraj, Rhino'dan Revit'e, render ve diğer modüller | Yol haritasında |

Kullanıcıya yönelik ayrıntılı liste: [Mevcut Kapsam](plugin/docs/NELER-YAPABILIR.md). Değişiklik kayıtları:
[CHANGELOG.md](CHANGELOG.md).

> **Pilot dönemi:** Yeni katman şu anda yalnızca `dev` kanalında yer almaktadır. Pilot dönemi boyunca toplanan
> gerçek isteklerle yapılacak sınamanın ardından tüm kullanıcılara açık `main` kanalına aktarılacaktır. Bu nedenle
> aşağıdaki `main` kurulum satırı da o tarihe kadar çalışmaz.

## Çalışma ilkesi: istek karşılama katmanı

İstekler kullanıcının kendi ifadeleriyle yazılır; "skill" ya da "plan" gibi terimlerin bilinmesi gerekmez. Ön kapı
isteği karşılar, iş türünü tanır ve ajanı ilgili iş prosedürüne yönlendirir.

```mermaid
flowchart LR
    A["İstek<br/>'A blok zemin kata kapı koy'"] --> B["Ön kapı kartı<br/>(her istekte çalışan kanca)"]
    B --> C["istek-karsilama skill'i<br/>ilgili iş kartını okur"]
    C --> D{"Gereken program<br/>bu oturumda bağlı mı?"}
    D -- Hayır --> E["Durumu bildirir,<br/>/aec:kontrol-et önerir"]
    D -- Evet --> F["Proje bilgisini okur<br/>(CLAUDE.md, .aec/proje.md)"]
    F --> G["En fazla 3 soru<br/>+ VARSAYIM'lı plan"]
    G --> H{"Onay?"}
    H -- Evet --> I["Kopya dosyada uygular,<br/>sonra geri okur"]
    H -- Hayır --> G
```

- **Az sor, çok göster:** Önce proje dosyası incelenir; yalnızca en kritik eksikler (en fazla 3) sorulur, diğerleri
  planda **VARSAYIM** olarak belirtilir.
- **Desteklenmeyen işlerde bilgilendirme:** Gerekli araç bağlı değilse ya da iş henüz desteklenmiyorsa tahmine dayalı
  sonuç üretilmez; nedeni ve izlenecek sonraki adım bildirilir.
- **Kart, istek metnini içermez:** Müşteri e-postasından ya da çizimden aktarılan metin talimat olarak
  değerlendirilmez.
- **Cowork'te** her istekte çalışan kanca her zaman devreye girmeyebilir; bu durumda skill kendi açıklamasına göre
  seçilir.

### İş kartları

| İş türü | Durum | Ön kapının sorduğu kritik eksikler |
|---|---|---|
| Revit modelleme | Revit bağlantısı kurulu bilgisayarlarda kullanılabilir | kopya model mi, kat/seviye, aile ve tip, ölçü kaynağı |
| DWG okuma/aktarma | Yakında (Faz 1B) | hangi dosya ve pafta, hangi katmanlar, birim ve ölçek, DWG–Revit hizası |
| DWG'de çizim | Yakında | yeni dosya mı kopya mı, katman standardı, ölçek, yazı stili |
| Metraj/liste | Revit'ten kısmen kullanılabilir; DWG'den yakında | kaynak Revit mi DWG mi, net mi brüt mü, Excel biçimi, poz no (fiyatsız) |
| Rhino'dan Revit'e | Yakında (Rhino.Inside.Revit üzerine kod) | hangi geometri, Revit'te hangi kategori, birim ve orijin |
| Asma tavan | Yakında (Faz 1D) | hangi DWG ve oda, tavan sistemi, kot, kopya model mi |
| Render/görsel | Yakında; sahne tarifi ya da istem metni hazırlanabilir | hangi görünüş, stil, gizlilik (müşteri çizimi) |

Kart dosyaları: [plugin/skills/istek-karsilama/kartlar/](plugin/skills/istek-karsilama/kartlar/). Önerilen ve eksik
istek örnekleri: [Örnek İstekler](plugin/docs/ORNEK-ISTEKLER.md).

### Komutlar

| Komut | İşlev | Dosya yazar mı? |
|---|---|---|
| `/aec:kontrol-et` | uv, otomatik güncelleme, proje dosyaları ve Revit/AutoCAD/Rhino bağlantılarının durumunu Türkçe olarak raporlar; her eksik için yapılması gerekeni belirtir. Bir program yalnızca aracı oturumda mevcutsa ve yanıt veriyorsa "bağlı" olarak raporlanır. | Hayır |
| `/aec:proje-baslat` | En fazla 6 soruyla projenin `.aec/proje.md` dosyasını oluşturur ve `CLAUDE.md` dosyasına kısa bir bölüm ekler. Kullanıcı (ev) klasörüne ya da sürücü köküne yazmaz; dosyadaki mevcut metne dokunmaz. | Evet, proje klasörüne |
| `/aec:yardim` | Kullanımdaki özellikleri ve örnek istekleri gösterir. | Hayır |

## Kurulum

Terminal ve Cowork için ekran adlarını da içeren adım adım kurulum:
[Kurulum ve İlk Kullanım](plugin/docs/BASLA.md).

**Gereksinimler:** Windows 10/11, kişisel Claude Pro ya da Max hesabı, Claude Code (terminal) ya da Claude masaüstü
uygulamasında Cowork. Ofiste Revit 2027, AutoCAD 2027 ve Rhino 8 kullanılmaktadır. uv ve Python 3.12, kurulum betiği
tarafından kurulur.

**Pilot (dev) kanalı** için aşağıdaki satır Win+R ya da `cmd` penceresine yazılır:

```
powershell -ExecutionPolicy Bypass -c "$env:AEC_KANAL='dev'; iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/dev/kur.ps1).TrimStart([char]0xFEFF))"
```

**Kararlı (main) kanal** satırı, değişiklikler `main` dalına aktarıldıktan sonra çalışır:

```
powershell -ExecutionPolicy Bypass -c "iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
```

Kurulum betiği (`kur.ps1`) sırasıyla şu işlemleri yapar:

1. uv'yi kurar (winget ile; winget bulunmuyorsa resmî kurulum betiğiyle).
2. Python 3.12'yi indirir; böylece ilk oturumda bekleme yaşanmaz.
3. Bilgisayarda Claude Code (terminal) kuruluysa marketplace'i ekler, `aec` eklentisini kurar ve otomatik
   güncellemeyi açar. Bu işlemden önce ayar dosyasını yedekler (`settings.json.aec-yedek`); diğer ayarları
   değiştirmez.
4. Claude Code bulunmuyorsa (Cowork kullanımı) eklenti adımını atlar ve Cowork kurulum adımlarına yönlendirir.
5. Revit bileşenlerinin (pyRevit ve Revit MCP eklentisi) durumunu yalnızca raporlar; kurulum yapmaz.

Yapılacak işlemleri önceden görüntülemek için `-KuruCalistir` parametresi ya da `$env:AEC_KURU='1'` kullanılır (bu
modda hiçbir şey kurulmaz).

**Cowork:** Aynı kurulum satırı çalıştırıldıktan sonra Customize > Plugins > Add marketplace >
`modularbelen-del/aec-harness` yolu izlenir ve "Sync automatically" seçeneği açılır. Yerel program bağlantıları için
oturumun "bilgisayarınızda" seçeneğiyle başlatılması gerekir. Ayrıntılar: [Kurulum ve İlk Kullanım](plugin/docs/BASLA.md).

İlgili belgeler: [Güvenlik İlkeleri](plugin/docs/GUVENLIK.md), [Sorun Giderme](plugin/docs/SORUN-GIDERME.md),
[Sözlük](plugin/docs/SOZLUK.md).

### Elle kurulum (sistem yöneticileri için)

`C:\Users\<kullanıcı>\.claude\settings.json` dosyasına aşağıdaki anahtarlar eklenir. Dosyada başka ayarlar
bulunuyorsa bu anahtarlar mevcut ayarların yanına yerleştirilir. Claude Code bir sonraki açılışta eklentiyi indirir,
kurar ve güncel tutar. uv ayrıca kurulmalıdır (`winget install --id=astral-sh.uv -e`).

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

Otomatik güncelleme kapalı görünüyorsa `/plugin` > Marketplaces > aec-office > Enable auto-update yolu izlenir.

## Kanallar

- `main`: tüm kullanıcılar için kararlı kanal. Korumalıdır; yalnızca PR ile değiştirilir.
- `dev`: pilot kullanıcılar için deneme kanalı. Kurulum: [Kurulum ve İlk Kullanım, Kanallar bölümü](plugin/docs/BASLA.md#kanallar).

İki kanalın marketplace adı aynı olduğundan iki kanal aynı bilgisayarda birlikte kurulamaz. Eklentide `version` alanı
bulunmaz; her commit yeni bir sürüm sayılır ve otomatik güncellemeyle ilgili kanaldaki tüm kullanıcılara ulaşır.

## Güvenlik ilkeleri (özet)

Eklenti bu kurallara göre çalışacak şekilde yapılandırılmıştır; yine de izin ekranları okunmalı ve emin olunamayan
durumlarda istek reddedilmelidir.

- Orijinal DWG ve RVT dosyalarına yazılmaz; işlemler kopya dosyada yapılır.
- Kaydetme ve merkez modelle eşitleme (sync) yalnızca kullanıcı tarafından yapılır.
- Müşteri çizimleri ücretsiz yapay zekâ sitelerine yüklenmez.
- Bakanlık birim fiyatları kullanılmaz; metrajda yalnızca poz numarası yazılır.
- Çizimde ya da e-postada yer alan metin talimat olarak değil, veri olarak değerlendirilir.
- Repoya gerçek proje, müşteri ya da dosya adı eklenmez (repo herkese açıktır).

## Rol ve ofis kuralları

Eklenti her oturumun başında iki dosyayı Claude'un bağlamına ekler:

- `plugin/standards/rol.md`: ajanın rolü ve çalışma biçimi (30 yıl deneyimli mimar). Ajan, Revit, AutoCAD ya da
  Rhino'ya yalnızca ilgili programın MCP aracı oturumda varsa bağlanır; araç yoksa bağlantının kurulu olmadığını
  bildirir ve `/aec:kontrol-et` komutunu önerir.
- `plugin/standards/authority.md`: çelişki durumunda hangi kaynağın geçerli olduğu (yetki sırası: çizim → proje
  kuralları → ofis standartları → araştırma kataloğu) ve "az sor, çok göster" kuralı.

Windows'ta ayrıca Revit, AutoCAD ve Rhino'dan hangilerinin açık olduğu tek satırlık bir ipucu olarak eklenir. Bu satır
bağlantının kurulu olduğu anlamına gelmez. Bu dosyalardaki değişiklikler PR ile yapılır; birleştirilen değişiklik
ilgili kanaldaki tüm kullanıcılara bir sonraki açılışta ulaşır.

## Repo yapısı

```
.claude-plugin/marketplace.json   marketplace tanımı (aec-office)
kur.ps1, kur.cmd                  kurulum betiği (BOM'lu UTF-8) ve çift tıklamayla çalışan başlatıcısı
CHANGELOG.md                      Türkçe değişiklik günlüğü
plugin/
  .claude-plugin/plugin.json      eklenti tanımı (aec)
  hooks/                          SessionStart (kurallar + program ipucu) ve UserPromptSubmit (ön kapı) kancaları
    onkapi.py                     Türkçe normalleştirme, anahtar kelime eşleştirme, kart metni, oturum başına tekrar engeli
  skills/
    istek-karsilama/              ön kapı skill'i, kartlar.json (anahtar kelimeler) ve kartlar/*.md (iş kartları)
    kontrol-et/, proje-baslat/, yardim/   komutlar
  scripts/                        komutların standart kütüphaneyle yazılmış Python betikleri
  standards/                      rol.md ve authority.md
  docs/                           kullanıcı belgeleri (Türkçe)
  evals/                          ön kapının sentetik eval seti (claude plugin eval)
  src/aec/                        geometri çekirdeği (eğri, tavan geometrisi)
tests/                            pytest testleri (CI'da Windows'ta çalışır)
docs/spikes/                      teknik deneme notları
```

## Geliştirme (bakımcılar için)

```powershell
uv sync --project plugin                 # ortamın kurulumu
uv run --project plugin pytest -q        # testler
claude plugin validate .                 # marketplace manifesti
claude plugin validate plugin            # plugin manifesti
```

- **Testler:** Kancalar, ön kapı eşleştirmesi (Türkçe karakterli ve karaktersiz yazım, ekler, yanıltıcı kelimeler),
  kartlar ile belgelerin tutarlılığı, kurulum betiğinin kuru çalıştırması ve ayar düzenlemesi (geçici dosyalarda) ile
  komut betikleri test edilir. Kanca komutları `uv` bulunmadığında da hata vermeden sonlanır (`; exit 0`).
- **CI:** `main` ve `dev` dallarına yapılan her push'ta ve her PR'da Windows üzerinde pytest ve
  `claude plugin validate` çalıştırılır.
- **Eval:** Ön kapının davranışı `claude plugin eval` ile sınanır. Komut, bütçe ve dikkat edilmesi gereken noktalar:
  [plugin/evals/README.md](plugin/evals/README.md). Eval, çalıştıran kişinin Claude hesabıyla yerel olarak çalışır;
  CI'da çalıştırılmaz.
- **Kurulum betiği test edilirken** gerçek modda çalıştırılmamalıdır; yalnızca `-KuruCalistir`/`AEC_KURU=1` ya da
  `AEC_SADECE_YUKLE=1` ile ve geçici dosyalar üzerinde çalıştırılır.

## Değişiklik akışı

Geliştirme `dev` dalında yürütülür. Pilot sürecinde sınanarak olgunlaşan değişiklikler PR ile `main` dalına aktarılır.
`main` dalına yapılan her push, bir sonraki açılışta tüm kullanıcılara ulaşır. Bu nedenle `main` korumalıdır: PR
açılır ve CI'daki `test` kontrolü başarılı olmadan birleştirme yapılmaz. Değişiklikler [CHANGELOG.md](CHANGELOG.md)
dosyasına kaydedilir.

Koruma kuralı repo ayarlarından bir kez tanımlanır (Settings → Branches → *Add classic branch protection rule*):

- *Branch name pattern*: `main`
- **Require a pull request before merging** işaretlenir. Altında otomatik olarak işaretlenen **Require approvals**
  seçeneği kaldırılır. Repo tek bakımcı tarafından yönetildiği sürece bu seçenek açık kalırsa, GitHub kişinin kendi
  PR'ını onaylamasına izin vermediğinden her birleştirmede korumanın atlanması gerekir. İkinci bir bakımcı
  katıldığında bu seçenek açılır.
- **Require status checks to pass before merging** işaretlenir ve listeden `test` seçilir.
- **Create** ile kaydedilir.

## Yol haritası

| Faz | İçerik | Durum |
|---|---|---|
| 1A | Geometri çekirdeği, açılış kancası, marketplace iskeleti | Tamamlandı (`main`) |
| 1A+ | Başlangıç katmanı: ön kapı, kartlar, komutlar, kurulum, belgeler, eval | Tamamlandı (`dev`, pilot aşamasında) |
| Bağlantılar ve ön koşullar | Revit MCP (ofis fork'u), AutoCAD MCP, Rhino MCP (rhinomcp); .NET 8, .NET 10, pyRevit kurulumu | Sıradaki plan |
| 1B | DWG okuma çekirdeği (AutoCAD Core Console → DXF → ezdxf) | Planlandı |
| 1C | Revit köprüsü: plan → tek işlem grubu → geri okuma → toleransla doğrulama; kontrol ve güvenlik kancası | Planlandı |
| 1D | Asma tavan modülü ve pilot | Planlandı |

1D'den sonra planlanan modüller: AutoCAD çizim ve detay, çizim tutarlılık kontrolleri, metraj ve mahal listeleri,
model sağlığı ve pafta kontrolü, Rhino.Inside.Revit ile Rhino'dan Revit'e, mevzuat (İmar, Yangın, Gürültü, Otopark,
Sığınak), Dijital Proje Yönetmeliği (yürürlük 01.09.2027), Revit aileleri, akustik, parametrik tasarım.

## Lisans

MIT lisansı ile dağıtılmaktadır. Ayrıntılar [LICENSE](LICENSE) dosyasında yer almaktadır. Telif hakkı © 2026
BelenPartners.
