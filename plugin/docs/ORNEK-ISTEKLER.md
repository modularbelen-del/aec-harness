# Örnek İstekler

İstek ne kadar açık yazılırsa o kadar az soru sorulur. Her işte aynı sıra izlenir: en fazla 3 soru, ardından varsayımları içeren plan, onaydan sonra uygulama ve son olarak geri okuma.

Varsayım, sorulmadan doğru kabul edilen bilgidir. Planda **VARSAYIM** etiketiyle işaretlenir; hatalı bir varsayım onaydan önce düzeltilmelidir. ([Sözlük](SOZLUK.md))

Her başlığın altında önce ilgili işin güncel durumu belirtilmiştir. Aşağıdaki adlar örnek amaçlıdır; isteklerde ilgili projenin ve katların gerçek adları kullanılmalıdır.

"Ön kapının sorabileceği bilgiler" listesi, ilgili işte eksik olabilecek bilgileri gösterir. İstek karşılama katmanı (ön kapı) bunların tamamını sormaz; proje dosyasından ve açık modelden bulabildiklerini kendisi tamamlar, kalanlardan en önemli üçünü sorar.

## Revit modelleme

**Durum:** Revit bağlantısı kurulu bilgisayarlarda kullanılabilir (bağlantı durumu `/aec:kontrol-et` ile görüntülenebilir).

**Eksik istek:** `Duvarları çiz.`

**Önerilen istek:** `Revit'te Zemin kat'a, A blok planındaki ölçülerle iç duvarları kopya modelde oluştur.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- kopya model mi
- kat/seviye
- aile ve tip
- ölçü kaynağı

## DWG okuma/aktarma

**Durum:** Yakında (Faz 1B). Şu aşamada ölçüler kullanıcı tarafından verilirse plan hazırlanabilir.

**Eksik istek:** `Şu çizimi Revit'e at.`

**Önerilen istek:** `A blok DWG dosyasındaki duvar ve kolon katmanlarını oku. Birim milimetre. Önce ne bulduğunu listele.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- hangi dosya ve pafta
- hangi katmanlar
- birim ve ölçek
- DWG–Revit hizası

## DWG'de çizim

**Durum:** Yakında.

**Eksik istek:** `Detay çiz.`

**Önerilen istek:** `Yeni bir DWG dosyasında, 1/20 ölçekte, kapı eşiği detayını çiz. Orijinal dosyaya dokunma.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- yeni dosya mı kopya mı
- katman standardı
- ölçek
- yazı stili

## Metraj/liste

**Durum:** Revit bağlıysa Revit'ten kısmen kullanılabilir; DWG kaynağı için yakında.

**Eksik istek:** `Metraj çıkar.`

**Önerilen istek:** `Zemin kat'taki odaların alanlarını mahal listesi olarak Excel tablosuna yaz. Birim metrekare.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- kaynak Revit mi DWG mi
- net mi brüt mü
- Excel biçimi
- poz no (fiyatsız)

## Rhino'dan Revit'e

**Durum:** Yakında.

**Eksik istek:** `Rhino'daki şeyi Revit'e geçir.`

**Önerilen istek:** `Rhino'daki cephe panellerini A blok Revit modelinin kopyasına aktar.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- hangi geometri
- Revit'te hangi kategori
- birim ve orijin

## Asma tavan

**Durum:** Yakında (Faz 1D).

**Eksik istek:** `Tavanı yap.`

**Önerilen istek:** `Zemin kat koridorunun asma tavanını DWG tavan planından kopya modelde oluştur.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- hangi DWG ve oda
- tavan sistemi
- kot
- kopya model mi

## Render/görsel

**Durum:** Yakında. Şu aşamada sahne tarifi ya da istem metni hazırlanabilir.

**Eksik istek:** `Güzel bir görsel yap.`

**Önerilen istek:** `A blok girişinin gündüz, insan gözü yüksekliğinde bir perspektif görseli için sahne tarifi yaz.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur):

- hangi görünüş
- stil
- gizlilik (müşteri çizimi)
