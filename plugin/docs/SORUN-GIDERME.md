# Sorun Giderme

Eklenti beklendiği gibi çalışmadığında neden çoğunlukla bir bağlantı ya da kurulum eksikliğidir. İlk adım olarak `/aec:kontrol-et` komutu çalıştırılmalıdır; komut eksik bileşenleri raporlar.

## "Revit bağlı değil"

Revit bağlantısı yalnızca ofis tarafından kurulum yapılmış bilgisayarlarda çalışır. Aşağıdaki noktalar kontrol edilmelidir:

1. Revit ve ilgili proje açık mı?
2. Cowork kullanılıyorsa oturum "bilgisayarınızda" seçeneğiyle mi başlatıldı? ([Kurulum ve İlk Kullanım](BASLA.md))
3. Sorun devam ediyorsa `/aec:kontrol-et` çıktısı ofisteki sistem sorumlusuna iletilmelidir.

AutoCAD ve Rhino bağlantıları henüz kullanıma sunulmamıştır; bu programlar için "bağlı değil" mesajı beklenen bir durumdur. ([Mevcut Kapsam](NELER-YAPABILIR.md))

## "hook error"

Oturum açılışında ya da bir istekten sonra "hook error" uyarısı görüntülenirse ([hook](SOZLUK.md)) neden genellikle aşağıdakilerden biridir:

- İlk açılışta yardımcı program gerekli dosyaları indirirken süre aşımı yaşanmıştır. Sorun genellikle ikinci açılışta giderilir.
- Cowork ortamı yardımcı programı çalıştıramamıştır.

(`uv` kurulu değilse bu uyarı görüntülenmez; bu durumda ön kapı kartı herhangi bir uyarı olmadan gelmez. Bu durum için aşağıdaki "uv bulunamadı" bölümüne başvurulabilir.)

Yapılması gerekenler:

1. Oturum kapatılıp yeniden açılır.
2. Sorun sürerse [Kurulum ve İlk Kullanım](BASLA.md) sayfasındaki tek satırlık kurulum yeniden çalıştırılır.
3. Sorun yine giderilemezse ofisteki sistem sorumlusuna bilgi verilir.

Bu süre içinde istekler çoğu durumda işlenmeye devam eder; yalnızca istek karşılama katmanının (ön kapı) kartı gelmez. İstekler işlenmiyorsa `/aec:kontrol-et` komutu çalıştırılmalıdır.

## "uv bulunamadı"

[uv](SOZLUK.md), eklentinin yardımcı betiklerini çalıştıran programdır. Kurulum için:

- Terminal kullanılıyorsa [Kurulum ve İlk Kullanım](BASLA.md) sayfasındaki kurulum satırı yeniden çalıştırılır.
- Cowork kullanılıyorsa aynı kurulum satırı çalıştırılır. Repo klasörünün tamamı indirilmişse `kur.cmd` dosyasına çift tıklanarak da kurulum yapılabilir.

Ardından Claude kapatılıp yeniden açılır.

## Ön kapı kartı görüntülenmiyor (Cowork)

Cowork'te ön kapı kartı her istekte görüntülenmeyebilir; bu bir hata değildir. İstek normal biçimde yazılır; eklenti çoğu durumda yine devreye girer. Devreye girmezse `/aec:kontrol-et` komutu çalıştırılmalıdır.

Eklenti hiç yanıt vermiyorsa şu noktalar kontrol edilir:

1. Customize > Plugins bölümünde `aec` eklentisi etkin mi?
2. Marketplace için "Sync automatically" seçeneği açık mı?
3. Ardından yeni bir oturum başlatılır.

## Otomatik güncelleme kapalı görünüyor

`/plugin` komutu çalıştırılarak Marketplaces > aec-office > Enable auto-update yolu izlenir.

## Revit'e yazma reddedildi ya da onay kaydedilmedi

Eklenti onay kaydını ve Revit'e yazmayı kodla denetler. Aşağıdaki bildirimler bu denetimden gelir; bir arıza değildir.

- **"Bu mesaj onay olarak kaydedilmedi":** Onay sorusuna verilen yanıt soru işareti, şart ya da ek bir açıklama içerdiği için onay sayılmamıştır (ör. "evet ama önce kapıyı 90 yap", "olur mu?"). Varsa soru ya da değişiklik isteği ayrı bir mesajla yazılır. Belge yeniden sunulduğunda yanıt olarak yalnızca "evet" yazılır.
- **"Bu oturuma bağlı bir iş bulunmadığından mesajınız onay olarak kaydedilmedi":** Onay ya da kabul bekleyen iş önceki bir oturumda açılmıştır ve bu oturuma henüz bağlanmamıştır. Ajan işi `devam` komutuyla bu oturuma bağlar ve belgeyi yeniden sunar; yanıt olarak yine yalnızca "evet" ya da "hayır" yazılır.
- **"Revit'e yazma işlemi için onaylanmış bir iş kaydı bulunmamaktadır":** Bu oturuma bağlı ve planı onaylanmış bir iş yoktur. Plan henüz onaylanmamışsa ya da onay kaydedilmemişse ajandan planı yeniden onaya sunması istenir ve yanıt olarak yalnızca "evet" yazılır. İş önceki bir oturumda açılmışsa ajandan işe `devam` komutuyla devam etmesi istenir; önceki oturumda verilmiş plan onayı bu oturumda yeniden sorulur. İş kontrol ya da kabul aşamasındaysa yeni yazma yapılmaz; değişiklik gerekiyorsa kabul sorusuna "hayır" yazılır ve gerekçe belirtilir.
- **Kaydetme ya da eşitleme reddedildi:** Model, kontrol raporu incelenip iş kabul edildikten sonra kaydedilebilir. Modeli kaydederek kapatma da kaydetme sayılır. Merkez modelle eşitleme aracı eklenti tarafından her zaman reddedilir; eşitleme Revit'te kullanıcı tarafından yapılır.
- **"İş kaydı okunamadı":** İşin kayıt dosyası (`.aec/isler/` altında) okunamadığı için yazma güvenlik nedeniyle durdurulmuştur. Kayıt dosyası elle düzenlenmez; durum ofisteki sistem sorumlusuna iletilir.
- **"Eklenti bileşeni yüklenemedi":** Eklentinin bir dosyası yüklenemediği için Revit'e yazma güvenlik nedeniyle durdurulmuştur. `/aec:kontrol-et` komutu çalıştırılır; sorun sürerse [Kurulum ve İlk Kullanım](BASLA.md) sayfasındaki kurulum yeniden yapılır ya da ofisteki sistem sorumlusuna bilgi verilir.

## Sorun devam ediyorsa

Ekrandaki hata metni kopyalanır ve yazılan istek eklenir. Metinde müşteri bilgisi varsa çıkarılır. Hazırlanan metin ofisteki sistem sorumlusuna iletilir.
