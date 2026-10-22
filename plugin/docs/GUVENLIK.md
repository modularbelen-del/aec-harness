# Güvenlik İlkeleri

Bu ilkeler, ofisin ve müşterilerin bilgilerini korumak amacıyla belirlenmiştir. Eklenti bu ilkelere göre çalışacak şekilde yapılandırılmıştır. Ancak yapay zekâ hata yapabilir; yapılandırma tek başına güvence sağlamaz. Bu nedenle izin ekranını okuyunuz ve ilkelere siz de uyunuz.

## 1. Orijinal dosyaya yazılmaz

Orijinal DWG ve RVT dosyalarına yazılmaz. Eklenti yalnızca kopya ya da yeni dosyada çalışacak şekilde yapılandırılmıştır; merkez model ya da müşteri çizimi üzerinde doğrudan işlem yapmaması öngörülmüştür. Yine de izin ekranını okuyunuz: hangi dosyaya yazılacağı bu ekranda belirtilir. Ekranda orijinal dosyanın adı yer alıyorsa isteği reddediniz. Kopya dosyanın kontrol edilmesi ve orijinalin yerine konması kullanıcı tarafından yapılır.

## 2. Merkez modelle eşitleme yalnızca kullanıcı tarafından yapılır

Merkez modelle eşitleme (sync) tüm ekibi etkiler; bu nedenle yalnızca kullanıcı tarafından yapılır. Eklentinin Revit kilidi eşitleme aracını (`sync_with_central`) her zaman reddeder. Kaydetme aracı (`save_document`) iş sizin tarafınızdan kabul edilmeden reddedilir; kabulden sonra da yalnızca siz açıkça isterseniz kullanılacak şekilde yapılandırılmıştır. İzin ekranında eşitleme (sync) ya da talep etmediğiniz bir kaydetme (save) işlemi yer alıyorsa isteği reddediniz.

## 3. Revit'e yazma kilidi

Revit'e yazan araçlar her çağrıdan önce eklentinin kancası tarafından denetlenir. Bu denetim ajanın talimatlarından bağımsız olarak kodla yapılır.

| İşlem | Ne zaman çalışır |
|---|---|
| Modeli değiştiren araçlar (`execute_revit_code`, `place_family`) ve belge kapatma (`close_document`) | Yalnızca bu oturumda açılmış işin planı (karmaşık işte görevleri) onaylandıktan sonra, kontrol raporu kaydedilene kadar |
| Kaydetme (`save_document`) | Yalnızca iş sizin tarafınızdan kabul edildikten sonra |
| Merkez modelle eşitleme (`sync_with_central`) | Hiçbir zaman |

- Bu oturumda açılmış bir iş yoksa ya da iş kaydı okunamazsa Revit'e yazma reddedilir.
- `execute_revit_code` aracı okuma amacıyla kullanılsa da yazma sayılır.
- Onay ve kabul yalnızca sizin kısa "evet" mesajınızla kaydedilir; ret için "hayır" yazılır. Soru işareti, şart ya da ek açıklama içeren bir mesaj onay sayılmaz.
- Ajanın onay ya da kabul verebileceği bir komut yoktur. İş kayıtlarının tutulduğu `.aec/isler/` klasörüne dosya düzenleme araçlarıyla yazma da reddedilir.
- DWG, Excel ve render işlerinde kod düzeyinde bir kilit yoktur. Bu işlerde de aynı akış izlenir, ancak denetim ajanın talimatlarına dayanır; izin ekranı bu işlerde daha dikkatli incelenmelidir.

**Cowork'te kancalar çalışmadığında:** Onay bu oturumda kaydedilemez. Revit'e yazmadan önce "Onay kaydı bu oturumda doğrulanamadı. Bu yazma işlemini onaylıyor musunuz?" açıklamalı bir izin ekranı açılabilir. Bu ekranda yapılacak işlem onayladığınız planla karşılaştırılır; uyumluysa onay verilir. Bağımsız kontrol ve kabul bu oturumda kaydedilmez. Kancaların hiç çalışmadığı bir oturumda kod düzeyindeki kilit de devreye girmez; bu durumda izin ekranında eşitleme (sync) ya da talep etmediğiniz bir kaydetme (save) işlemi yer alıyorsa isteği reddediniz.

## 4. Korumanın sınırı

Revit kilidi ve iş kayıtlarının korunması **kazara** yapılan hatalara karşı tasarlanmıştır: ajanın bir mesajı yanlışlıkla onay sayması, onaysız yazmaya başlaması ya da kendi işini onaylaması gibi. Bu korumalar **kasıtlı** bir aşmaya karşı tam güvence sağlamaz. Örneğin komut satırı araçları (Bash, PowerShell) tümüyle kapatılamadığından iş kayıtları bu yolla değiştirilebilir. Bu nedenle izin ekranının okunması ve plana uymayan işlemlerin reddedilmesi her durumda gereklidir.

## 5. Müşteri çizimleri ücretsiz yapay zekâ sitelerine yüklenmez

Müşteriye ait çizim, plan ve fotoğraflar herkese açık, ücretsiz yapay zekâ sitelerine yüklenmez ve ofisin onayladığı araçlar dışında hiçbir yere gönderilmez.

## 6. İzin ekranı görüntülendiğinde

Çalışma sırasında izin isteyen bir ekran görüntülenebilir. Bu ekran incelenmeden onaylanmamalıdır.

1. Ekrandaki açıklama okunur; yapılacak işlem burada belirtilir.
2. Açıklama, daha önce sunulan planla karşılaştırılır.
3. Plan ile uyumluysa onay verilir.
4. Uyumlu değilse ya da açıklama anlaşılır değilse istek **reddedilir** ve işlemin ne olduğu sorulur.

Emin olunamayan durumlarda reddetmek her zaman güvenli seçenektir.

## 7. Birim fiyatlar

Bakanlık birim fiyatları kullanılmaz. Fiyat gerektiğinde ofisin belirlediği fiyat listesi esas alınır.

## 8. Dışarıdan aktarılan metinler

Müşteri e-postasından ya da çizimden kopyalanan metinler gizli talimatlar içerebilir. Yapay zekâ bu tür bir talimatı kullanıcının isteği olarak yorumlayabilir. Kaynağı belirsiz metinlerin yapıştırılmaması önerilir; bu tür bir metin yapıştırıldıysa izin ekranı daha dikkatli incelenmelidir.
