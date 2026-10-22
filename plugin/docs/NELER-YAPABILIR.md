# Mevcut Kapsam

Eklenti erken geliştirme aşamasındadır. Bu sayfada kullanımdaki özellikler ve planlanan özellikler ayrı ayrı listelenmiştir. "Yakında" olarak belirtilen özellikler henüz kullanılamaz.

## Kullanımdaki özellikler

- **İstek karşılama katmanı (ön kapı):** İsteği tanıyarak önce plan sunar. Yedi iş türünü tanır: Revit modelleme, DWG okuma/aktarma, DWG'de çizim, Metraj/liste, Rhino'dan Revit'e, Asma tavan, Render/görsel. Basit işte en fazla 3 soru sorar; çizim ya da model değiştiren işte tam görüşme yapar. Varsayımları açıkça belirtir. Onay alınmadan değişiklik yapmayacak şekilde yapılandırılmıştır; yine de izin ekranını okuyunuz ([Güvenlik İlkeleri](GUVENLIK.md)). Cowork'te ön kapı kartı her istekte görüntülenmeyebilir; eklenti çoğu durumda yine devreye girer, girmezse `/aec:kontrol-et` komutu çalıştırılmalıdır.
- **İş akışı:** Her iş görüşme, kabul ölçütleri, plan onayı, uygulama, bağımsız kontrol ve kabul adımlarından geçer.
  - Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren iş karmaşık iştir: tam görüşme yapılır; tarif, plan ve görevler ayrı ayrı onayınıza sunulur. Diğer işlerde yalnızca plan onaylanır.
  - Onay, ret ve kabul kararları yalnızca sizin "evet" ya da "hayır" yanıtınızla verilir ve eklenti tarafından kaydedilir. Soru, şart ya da ek açıklama içeren bir yanıt onay sayılmaz.
  - Revit'e yazma, onaylanmış bir plan olmadan reddedilir (kancaların çalışmadığı Cowork oturumlarında yazma öncesinde izin ekranında onayınız istenebilir). Merkez modelle eşitleme her zaman reddedilir; kaydetme yalnızca iş kabul edildikten sonra yapılabilir. DWG, Excel ve render işlerinde bu kilit kod düzeyinde değildir; akış ajanın talimatlarıyla yürür.
  - Uygulamadan sonra bağımsız kontrolcü (`aec:dogrulayici`) kabul ölçütlerini denetler ve her ölçütü GEÇTİ, KALDI ya da DOĞRULANAMADI olarak raporlar. Rapor size sunulur; kabul kararı sizindir.
  - Kontrolcü bugün Revit'teki konum ve ölçü ölçütlerinin birçoğunu doğrulayamaz; bu ölçütler raporda DOĞRULANAMADI olarak gösterilir ve sizin tarafınızdan kontrol edilmelidir. Ölçü doğrulaması Revit köprüsü (Faz 1C) ile eklenecektir.
  - İş kayıtları proje klasöründeki `.aec/isler/` klasöründe, kabul ve ret kararları `.aec/gunluk.md` dosyasında tutulur.
- **`/aec:kontrol-et`:** Kurulumu ve Revit, AutoCAD, Rhino bağlantılarını kontrol eder; sorun varsa yapılması gerekeni belirtir.
- **`/aec:proje-baslat`:** Proje bilgileri birkaç soruyla bir kez kaydedilir; ajan bu bilgileri her istekte yeniden sormak yerine kaydedilen dosyadan okur.
- **`/aec:yardim`:** Bu sayfanın içeriğini gösterir.
- **Güvenlik ilkeleri:** Eklenti orijinal dosyaya yazmayacak ve eşitleme işlemini kullanıcıya bırakacak şekilde yapılandırılmıştır. Ayrıntılar: [Güvenlik İlkeleri](GUVENLIK.md).

**Revit:** Temel Revit bağlantısı (Revit durumunu ve seviyeleri okuma, aileleri listeleme, onaydan sonra yerleştirme) yalnızca ofis tarafından bu bağlantının kurulduğu bilgisayarlarda çalışır. Yakında eklenecek Revit köprüsü (Faz 1C), bu bağlantının üzerine onaylı planı uygulayan ve sonucu Revit'ten geri okuyarak kontrol eden bir araç ekleyecektir. AutoCAD ve Rhino bağlantıları yakında eklenecektir.

İstek yazım örnekleri [Örnek İstekler](ORNEK-ISTEKLER.md) sayfasında, kurulum adımları [Kurulum ve İlk Kullanım](BASLA.md) sayfasında yer almaktadır.

## Planlanan özellikler (yakında)

Aşağıdaki özellikler henüz kullanılamaz; tamamlanma tarihi belirtilmemiştir.

- DWG dosyasından okuma (Faz 1B)
- Revit köprüsü (Faz 1C): onaylı planı uygulayıp Revit'ten geri okuyarak doğrulayan araç (mevcut temel bağlantının üzerine eklenir); kontrolcünün ölçü ölçütlerini milimetre toleransla doğrulaması
- Yazma kilidinin AutoCAD ve Rhino bağlantılarına genişletilmesi
- Asma tavan üretimi (Faz 1D)
- AutoCAD'de çizim
- Rhino'dan Revit'e aktarma
- Metraj
- Render
- Bağlantı programlarının kuruluma eklenmesi
