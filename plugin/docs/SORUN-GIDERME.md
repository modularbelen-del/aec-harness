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

## Sorun devam ediyorsa

Ekrandaki hata metni kopyalanır ve yazılan istek eklenir. Metinde müşteri bilgisi varsa çıkarılır. Hazırlanan metin ofisteki sistem sorumlusuna iletilir.
