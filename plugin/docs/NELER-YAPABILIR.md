# Mevcut Kapsam

Eklenti erken geliştirme aşamasındadır. Bu sayfada kullanımdaki özellikler ve planlanan özellikler ayrı ayrı listelenmiştir. "Yakında" olarak belirtilen özellikler henüz kullanılamaz.

## Kullanımdaki özellikler

- **İstek karşılama katmanı (ön kapı):** İsteği tanıyarak önce plan sunar. Yedi iş türünü tanır: Revit modelleme, DWG okuma/aktarma, DWG'de çizim, Metraj/liste, Rhino'dan Revit'e, Asma tavan, Render/görsel. En fazla 3 soru sorar ve varsayımları açıkça belirtir. Onay alınmadan değişiklik yapmayacak şekilde yapılandırılmıştır; yine de izin ekranını okuyunuz ([Güvenlik İlkeleri](GUVENLIK.md)). Cowork'te ön kapı kartı her istekte görüntülenmeyebilir; eklenti çoğu durumda yine devreye girer, girmezse `/aec:kontrol-et` komutu çalıştırılmalıdır.
- **`/aec:kontrol-et`:** Kurulumu ve Revit, AutoCAD, Rhino bağlantılarını kontrol eder; sorun varsa yapılması gerekeni belirtir.
- **`/aec:proje-baslat`:** Proje bilgileri birkaç soruyla bir kez kaydedilir; ajan bu bilgileri her istekte yeniden sormak yerine kaydedilen dosyadan okur.
- **`/aec:yardim`:** Bu sayfanın içeriğini gösterir.
- **Güvenlik ilkeleri:** Eklenti orijinal dosyaya yazmayacak ve eşitleme işlemini kullanıcıya bırakacak şekilde yapılandırılmıştır. Ayrıntılar: [Güvenlik İlkeleri](GUVENLIK.md).

**Revit:** Temel Revit bağlantısı (Revit durumunu ve seviyeleri okuma, aileleri listeleme, onaydan sonra yerleştirme) yalnızca ofis tarafından bu bağlantının kurulduğu bilgisayarlarda çalışır. Yakında eklenecek Revit köprüsü (Faz 1C), bu bağlantının üzerine onaylı planı uygulayan ve sonucu Revit'ten geri okuyarak kontrol eden bir araç ekleyecektir. AutoCAD ve Rhino bağlantıları yakında eklenecektir.

İstek yazım örnekleri [Örnek İstekler](ORNEK-ISTEKLER.md) sayfasında, kurulum adımları [Kurulum ve İlk Kullanım](BASLA.md) sayfasında yer almaktadır.

## Planlanan özellikler (yakında)

Aşağıdaki özellikler henüz kullanılamaz; tamamlanma tarihi belirtilmemiştir.

- DWG dosyasından okuma (Faz 1B)
- Revit köprüsü (Faz 1C): onaylı planı uygulayıp Revit'ten geri okuyarak doğrulayan araç (mevcut temel bağlantının üzerine eklenir)
- Asma tavan üretimi (Faz 1D)
- AutoCAD'de çizim
- Rhino'dan Revit'e aktarma
- Metraj
- Render
- Bağlantı programlarının kuruluma eklenmesi
