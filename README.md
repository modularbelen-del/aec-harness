# aec-harness

Mimarlık ofisleri için geliştirilmiş bir Claude eklentisidir (Claude Code plugin marketplace: `aec-office`, eklenti:
`aec`). Revit, AutoCAD ve Rhino ile yürütülen günlük işler için hazırlanmıştır. İstekler gündelik dille yazılabilir;
eklenti işi tanır, eksik bilgileri sorar ve uygulamadan önce planı onaya sunar.

Hedef, ajanın ölçüleri görselden tahmin etmek yerine araçla okuması, Revit'e yalnızca onaylanmış bir plan üzerinden
ve kopya dosyada yazması, yazdıktan sonra da sonucu Revit'ten okuyarak toleransla karşılaştırmasıdır. Öngörülen iş
akışı: **ölç → planla → onayla → uygula → geri oku → doğrula**.

Bu akışın ilk katmanları kullanımdadır: isteği tanıyarak önce plan sunan **istek karşılama katmanı (ön kapı)**, onay
ve kabulü kodla kaydeden **iş akışı** (Revit yazma kilidi ve bağımsız kontrolcü ile), ofis kuralları ve üç komut.
Ölçü okuyan ve geri okumayı toleransla doğrulayan araçlar sonraki fazlarda eklenecektir. Kullanımdaki ve planlanan
bileşenler aşağıda ayrı ayrı belirtilmiştir.

## Durum

| Bileşen | Durum |
|---|---|
| İstek karşılama katmanı (isteği tanır, eksikleri sorar, plan sunar, onay bekler) | Kullanımda; `dev` kanalında, pilot aşamasında |
| İş akışı (görüşme, kabul ölçütleri, kodla kaydedilen onay ve kabul, Revit yazma kilidi, bağımsız kontrolcü) | Kullanımda; `dev` kanalında, pilot aşamasında |
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
    F --> G["Görüşme ve kabul ölçütleri<br/>(basit işte en fazla 3 soru)"]
    G --> P["Plan<br/>(karmaşık işte tarif, plan, görevler)"]
    P --> H{"Onay?"}
    H -- Evet --> I["Kopya dosyada uygular"]
    H -- Hayır --> P
    I --> J["Bağımsız kontrolcü<br/>raporu"]
    J --> K{"Kabul?"}
    K -- Evet --> L["Kayıt<br/>(.aec/gunluk.md)"]
    K -- Hayır --> P
```

Onaydan sonraki adımlar aşağıdaki "İş akışı" bölümünde açıklanmıştır.

- **Az sor, çok göster:** Önce proje dosyası incelenir. Basit işte yalnızca en kritik eksikler (en fazla 3) sorulur,
  diğerleri planda **VARSAYIM** olarak belirtilir. Çizim ya da model değiştiren (karmaşık) işte tam görüşme yapılır;
  3 soru sınırı uygulanmaz.
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

## İş akışı

Her iş aynı yoldan geçer:

**görüşme → (karmaşık işte) tarif → plan ve kabul ölçütleri → kişinin onayı → uygulama → bağımsız kontrolcü →
kişinin kabulü → kayıt**

Onay ve kabul yalnızca kişinin kendi mesajından gelir ve kod (kanca) tarafından kaydedilir. Ajan kendi planını
onaylayamaz. Akışın ayrıntılı kuralları: [istek-karsilama skill'i](plugin/skills/istek-karsilama/SKILL.md).

### İşin sınıfı

İşin sınıfını sabit bir kural belirler ([karmasiklik.md](plugin/standards/karmasiklik.md)). Sınıf kişiye sorulmaz;
ajan gerekçesiyle bildirir.

- **Karmaşık iş:** Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren her iş. Küçük bir Revit
  düzeltmesi (ör. bir kapının tipini değiştirme) de bu sınıftadır.
- **Basit iş:** Çizim programına yazmayan iş: okuma, listeleme, kontrol, metraj ya da Excel raporu, soru-cevap, render
  tarifi.
- Basit görünen bir işin planı bir çizim programına yazmayı içeriyorsa iş, onaydan önce karmaşık sınıfına yükseltilir.

### Adımlar

| Adım | Basit iş | Karmaşık iş | Yürüten |
|---|---|---|---|
| 1. Kart ve araç kontrolü | İş kartı okunur; gereken programın bağlı olup olmadığına bakılır | Aynı | Ajan |
| 2. Görüşme | En fazla 3 soru, tek mesajda; kabul ölçütleri teklif edilir | Konu konu tam görüşme; her bölümde özet ve teyit; kabul ölçütleri görüşmede kesinleşir | Ajan ve kişi |
| 3. İş kaydı | İş açılır, kabul ölçütleri kaydedilir | Aynı | Ajan (iş kaydı aracı) |
| 4. Belgeler ve onay | Plan; tek onay | Tarif, plan ve görevler; her belge için ayrı onay | Ajan hazırlar, kişi onaylar, kanca kaydeder |
| 5. Uygulama | Onaylı plan kopya ya da yeni dosyada uygulanır | Görev görev | Ajan; Revit'te kilit kodla denetlenir |
| 6. Kontrol | `aec:dogrulayici` her ölçütü dener; raporu kanca kaydeder | Aynı | Kontrolcü ve kanca |
| 7. Kabul | Rapor gösterilir; kişi kabul eder ya da reddeder; ret durumunda plan gerekçeyle düzeltilip yeniden onaya sunulur | Aynı | Kişi; kanca kaydeder |
| 8. Kayıt | Karar `.aec/gunluk.md` dosyasına yazılır; kalıcı yeni bir bilgi varsa proje bilgilerine eklenmesi kişiye sorulur | Aynı | Kanca ve ajan |

Revit'e ilk başarılı yazmadan sonra iş, kod tarafından `uygulandi` durumuna geçirilir. Revit dışındaki işlerde bu
kaydı ajan, iş kaydı aracının `uygulandi` komutuyla yapar. Bu komut yalnızca onaylanmış bir planı ilerletir; onay
yerine geçmez.

### Onay ve kabulün verilmesi

Ajan belgeyi tam metniyle gösterir ve mesajını şu cümleyle bitirir: "Onaylıyorsanız yalnızca 'evet', reddediyorsanız
yalnızca 'hayır' yazınız." Kabul sorusu da aynı biçimde sorulur.

- Onay için yalnızca **"evet"**, ret için yalnızca **"hayır"** yazılır. Büyük-küçük harf ve Türkçe karakterli ya da
  karaktersiz yazım fark etmez.
- Mesaj soru işareti, şart ya da ek bir açıklama içeriyorsa onay sayılmaz (ör. "evet ama önce kapıyı 90 yap", "olur
  mu?", "tamam anladım"). İş kaydı değişmez; ajan mesajı yanıtlar ve onayı yeniden ister.
- Onay ya da kabul beklenmeyen bir anda yazılan "evet" hiçbir şeyi onaylamaz.
- Kabul aşamasında yalnızca açık kabul ifadeleri sayılır ("evet", "kabul ediyorum", "onaylıyorum"); "uygula" ya da
  "devam" kabul sayılmaz.
- Ajanın onay ya da kabul vermesi için bir komut yoktur: iş kaydı aracında (`is_kaydi.py`) onay ya da kabul komutu
  bulunmaz ve `.aec/isler/` klasörüne dosya düzenleme araçlarıyla (Write, Edit) yazma kodla reddedilir. Bu korumanın
  sınırı aşağıda "Korumanın sınırı" başlığında açıklanmıştır.

### Revit kilidi

Revit'e yazan araçlar her çağrıdan önce kodla denetlenir:

- Bu oturuma bağlı ve planı (karmaşık işte görevleri) onaylanmış bir iş yoksa `execute_revit_code`,
  `place_family` ve `close_document` reddedilir. Bu araçlar plan onaylandıktan sonra, kontrolcü raporu kaydedilene
  kadar çalışır. `execute_revit_code` okuma amacıyla kullanılsa da yazma sayılır. `close_document` iş kabul
  edildikten sonra da çalışır.
- `sync_with_central` (merkez modelle eşitleme) her zaman reddedilir; eşitlemeyi kişi yapar.
- `save_document` (kaydetme) yalnızca iş kişi tarafından kabul edildikten sonra çalışır. `close_document` kaydetme
  seçeneğiyle çağrılırsa kaydetme sayılır.
- İş kaydı okunamazsa ya da eklentinin bir bileşeni yüklenemezse Revit'e yazma durdurulur.
- DWG, Excel ve render işlerinde kod düzeyinde bir kilit yoktur; bu işlerde akış skill kurallarıyla yürür. AutoCAD ve
  Rhino bağlantıları eklendiğinde kilidin bu araçlara genişletilmesi planlanmaktadır.

### Bağımsız kontrolcü

Uygulamadan sonra ajan, bağımsız kontrolcü `aec:dogrulayici` ajanını çalıştırır.

- Kontrolcüye yalnızca iş klasörünün yolu verilir; başka bir istemle yapılan çağrı kodla reddedilir. Kontrolcü işin
  bağlamını uygulayan ajandan değil, iş klasöründeki dosyalardan okur.
- Dosya düzenleme araçları kontrolcüye kapalıdır ve Revit'te yalnızca okuma araçlarına erişebilir. Bash'i yalnızca
  okuma için kullanacak şekilde yönlendirilmiştir.
- Her kabul ölçütü kendi yöntemiyle (`revit-okuma`, `dosya`, `olcu`, `kisi-gorsel`) denenir ve **GEÇTİ**, **KALDI**
  ya da **DOĞRULANAMADI** olarak raporlanır. Kanıtı olmayan bir ölçüt GEÇTİ sayılmaz. `kisi-gorsel` ölçütleri için
  kontrol listesi hazırlanır; kararı kişi verir.
- Rapor, uygulayan ajan tarafından değil kanca tarafından `.aec/isler/<kimlik>/dogrulama.md` dosyasına kaydedilir.
  Raporda sonuç satırı yoksa ya da kontrolcüye çalışırken ek mesaj gönderildiyse sonuç DOĞRULANAMADI olarak kaydedilir.
- Sonuç KALDI ya da DOĞRULANAMADI olduğunda da rapor kişiye gösterilir; uyarı belirgin biçimde yazılır ve kararı kişi
  verir.
- **Bugünkü sınır:** Revit okuma araçları sınırlı olduğundan konum ve ölçü gibi Revit ölçütlerinin birçoğu bugün
  DOĞRULANAMADI olarak raporlanır; bu ölçütlerin kişi tarafından kontrol edilmesi gerekir. Ölçü doğrulaması (milimetre
  toleransla geri okuma, `verify.py`) Faz 1C ile eklenecektir.

İş uygulandıktan sonra ajan kontrolcüyü çalıştırmadan durmak isterse bir kez uyarılır. İkinci denemede durmasına izin
verilir ve günlüğe "doğrulama yapılmadan durdu" satırı yazılır. Bu satır işin bittiğini değil, ajanın kontrolcüyü
çalıştırmadan durduğunu gösterir; iş açık kalabilir ve kontrol daha sonra yapılabilir. İş kişinin onayını ya da
kabulünü beklerken ajanın durması hiçbir zaman engellenmez.

### Kayıtlar

- İş kayıtları proje klasöründe `.aec/isler/<kimlik>/` altında tutulur: `is.json` (durum, kabul ölçütleri, sonuç ve
  her durum değişikliğinin kaynağı), `tarif.md`, `plan.md`, `gorevler.md` ve `dogrulama.md`. Kimlik tarih ve saatle
  başlar (ör. `20261022-1430-kapi-yerlestirme`).
- İş, onu açan oturuma bağlıdır (`.aec/isler/aktif-<oturum>.json`); kişinin "evet"i yalnızca kendi oturumundaki işi
  ilerletir. Yeni bir oturumun başında açık işler (en fazla üç) ajana bildirilir ve ajan devam etmeyi önerir. Kişi
  devam etmek isterse ajan işi `devam` komutuyla yeni oturuma bağlar. Önceki oturumda verilmiş plan onayı yeniden
  istenir: iş `onay-bekliyor:plan` durumuna alınır. Kişi işi sürdürmek istemezse iş `iptal` ile kapatılır.
  Kabulde reddedilen iş de açık iş olarak listelenir; modeldeki değişiklikler yeniden planlanana ya da iş
  kapatılana kadar durur.
- Kabul ve ret kararları ile ajanın kontrolcüyü çalıştırmadan durduğu işler `.aec/gunluk.md` dosyasına birer satır
  olarak yazılır. "doğrulama yapılmadan durdu" satırı işin bittiğini göstermez; iş açık kalabilir.
- `.aec/proje.md` dosyasının yapısı ve işlevi değişmemiştir. İş sırasında kalıcı yeni bir bilgi ortaya çıkarsa bu
  dosyaya eklenmesi kişiye sorulur ve yalnızca kişi onaylarsa eklenir.
- İş kaydı kullanıcı (ev) klasöründe ya da sürücü kökünde açılmaz; Claude'un projenin klasöründe başlatılması gerekir.

### Korumanın sınırı

Bu korumalar **kazara** yapılan hatalara karşı tasarlanmıştır: ajanın bir mesajı yanlışlıkla onay sayması, onaysız
yazmaya başlaması ya da kendi işini onaylaması gibi. Bu korumalar **kasıtlı** bir aşmaya karşı tam güvence
sağlamaz; örneğin komut satırı araçları (Bash, PowerShell) tümüyle kapatılamadığından iş kayıtları bu yolla
değiştirilebilir. Bu nedenle izin ekranları okunmalı ve plana uymayan işlemler reddedilmelidir
([Güvenlik İlkeleri](plugin/docs/GUVENLIK.md)).

### Kancalar çalışmadığında (yumuşak mod)

Cowork'te kancalar her oturumda çalışmayabilir. Bu durumda:

- Onay kaydedilemez; iş kaydı onay bekleyen durumda kalır. Ajan bunu kişiye bir kez bildirir ve akışı kişinin "evet"
  yanıtlarıyla skill kurallarına göre sürdürür.
- Revit'e yazmadan önce bir izin ekranı açılabilir ("Onay kaydı bu oturumda doğrulanamadı. Bu yazma işlemini
  onaylıyor musunuz?"); onay bu ekrandan verilir.
- Kancaların hiç çalışmadığı bir oturumda kod düzeyindeki kilit de devreye girmez; bu durumda koruma izin ekranına ve
  ajanın talimatlarına dayanır.
- Bağımsız kontrol ve kabul bu oturumda kaydedilmez. Ajan geri okumayı okuma araçlarıyla yapar ve sonucu, bağımsız
  kontrol raporu olmadığını belirterek gösterir.

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
- Revit'e yazma, onaylanmış bir plan olmadan kodla reddedilir (ayrıntılar: "İş akışı" bölümü).
- Merkez modelle eşitleme (sync) yalnızca kullanıcı tarafından yapılır; Revit kilidi bu aracı her zaman reddeder.
  Kaydetme, iş kabul edilmeden reddedilir; kabulden sonra da yalnızca kullanıcı açıkça isterse yapılacak şekilde
  yapılandırılmıştır.
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
bağlantının kurulu olduğu anlamına gelmez. Proje klasöründe açık iş varsa en fazla üçü de listelenir. İşin sınıfını
belirleyen kural (`plugin/standards/karmasiklik.md`) oturum başında yüklenmez; istek karşılama skill'i tarafından
okunur. Bu dosyalardaki değişiklikler PR ile yapılır; birleştirilen değişiklik
ilgili kanaldaki tüm kullanıcılara bir sonraki açılışta ulaşır.

## Repo yapısı

```
.claude-plugin/marketplace.json   marketplace tanımı (aec-office)
kur.ps1, kur.cmd                  kurulum betiği (BOM'lu UTF-8) ve çift tıklamayla çalışan başlatıcısı
CHANGELOG.md                      Türkçe değişiklik günlüğü
THIRD_PARTY_NOTICES.md            uyarlanan açık kaynak projelerin lisans bildirimleri
plugin/
  .claude-plugin/plugin.json      eklenti tanımı (aec)
  agents/dogrulayici.md           bağımsız ve salt okuyan kontrolcü (aec:dogrulayici)
  hooks/                          SessionStart (kurallar, program ipucu, açık işler), UserPromptSubmit (ön kapı, onay
                                  kaydı), PreToolUse (Revit kilidi), PostToolUse, Stop ve SubagentStop kancaları
    onkapi.py                     Türkçe normalleştirme, anahtar kelime eşleştirme, kart metni, oturum başına tekrar engeli
    onay.py                       kişinin mesajından onay, ret ve kabulün tanınması
  skills/
    istek-karsilama/              ön kapı skill'i, kartlar.json (anahtar kelimeler), kartlar/*.md (iş kartları),
                                  gorusme.md (görüşme rehberi) ve sablonlar/ (tarif, plan, görevler)
    kontrol-et/, proje-baslat/, yardim/   komutlar
  scripts/                        komutların ve iş kaydı aracının (is_kaydi.py) standart kütüphaneyle yazılmış betikleri
  standards/                      rol.md, authority.md ve karmasiklik.md
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
| 1A++ | İş akışı: görüşme, kabul ölçütleri, kodla kaydedilen onay ve kabul, Revit yazma kilidi, bağımsız kontrolcü | `dev` kanalında, pilot aşamasında |
| Bağlantılar ve ön koşullar | Revit MCP (ofis fork'u), AutoCAD MCP, Rhino MCP (rhinomcp); .NET 8, .NET 10, pyRevit kurulumu | Sıradaki plan |
| 1B | DWG okuma çekirdeği (AutoCAD Core Console → DXF → ezdxf) | Planlandı |
| 1C | Revit köprüsü: plan → tek işlem grubu → geri okuma → toleransla doğrulama; ölçü ölçütlerinin bağımsız kontrolcüye bağlanması (`verify.py`) | Planlandı |
| 1D | Asma tavan modülü ve pilot | Planlandı |

1D'den sonra planlanan modüller: AutoCAD çizim ve detay, çizim tutarlılık kontrolleri, metraj ve mahal listeleri,
model sağlığı ve pafta kontrolü, Rhino.Inside.Revit ile Rhino'dan Revit'e, mevzuat (İmar, Yangın, Gürültü, Otopark,
Sığınak), Dijital Proje Yönetmeliği (yürürlük 01.09.2027), Revit aileleri, akustik, parametrik tasarım.

## Lisans

MIT lisansı ile dağıtılmaktadır. Ayrıntılar [LICENSE](LICENSE) dosyasında yer almaktadır. Telif hakkı © 2026
BelenPartners.

Görüşme rehberi obra/superpowers projesinden, tarif, plan ve görev şablonları github/spec-kit projesinden Türkçeye
uyarlanmıştır. Her iki proje de MIT lisanslıdır; lisans metinleri [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
dosyasında yer almaktadır.
