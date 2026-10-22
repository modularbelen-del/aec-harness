# Örnek İstekler

İstek ne kadar açık yazılırsa o kadar az soru sorulur. Her iş aynı yoldan geçer: görüşme, kabul ölçütleri ve plan, onay, uygulama, bağımsız kontrol ve kabul. Basit işte en fazla 3 soru sorulur. Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren iş karmaşık iştir: tam görüşme yapılır; tarif, plan ve görevler ayrı ayrı onaya sunulur. Aşağıda önce iki örnek akış, ardından iş türlerine göre örnek istekler yer almaktadır.

Varsayım, sorulmadan doğru kabul edilen bilgidir. Planda **VARSAYIM** etiketiyle işaretlenir; hatalı bir varsayım onaydan önce düzeltilmelidir. ([Sözlük](SOZLUK.md))

Her başlığın altında önce ilgili işin güncel durumu belirtilmiştir. Aşağıdaki adlar örnek amaçlıdır; isteklerde ilgili projenin ve katların gerçek adları kullanılmalıdır.

"Ön kapının sorabileceği bilgiler" listesi, ilgili işte eksik olabilecek bilgileri gösterir. İstek karşılama katmanı (ön kapı) proje dosyasından ve açık modelden bulabildiklerini kendisi tamamlar. Basit işte kalanlardan en önemli üçünü sorar; karmaşık işte kalanların tamamı görüşmede ele alınır.

## Örnek akış: basit iş

**İstek:** `Zemin kat'taki odaların alanlarını mahal listesi olarak Excel tablosuna yaz. Birim metrekare.`

1. **Sınıf:** Ajan işin basit iş olduğunu gerekçesiyle bildirir: iş, çizim programına yazmamaktadır.
2. **Görüşme:** Eksik bilgiler için tek mesajda en fazla 3 soru sorulur (ör. alanların net mi brüt mü olacağı, Excel biçimi). Aynı mesajda kabul ölçütleri teklif edilir, örneğin:
   - Excel plandaki yeni dosya adıyla oluşturulmuştur; satır sayısı modeldeki oda sayısıyla aynıdır (dosya).
   - Ara toplamlar ve genel toplam modeldeki değerlerle tutar (dosya).
3. **Plan ve onay:** Ajan iş kaydını açar, ölçütleri kaydeder ve planı tam metniyle gösterir. Mesaj "Onaylıyorsanız yalnızca 'evet', reddediyorsanız yalnızca 'hayır' yazınız." cümlesiyle biter. Plan uygunsa yanıt olarak yalnızca `evet` yazılır; değişiklik isteniyorsa istek ayrı bir mesajla yazılır ve plan yeniden onaya sunulur.
4. **Uygulama:** Tablo yeni bir Excel dosyası olarak yazılır. Bu işte kod düzeyinde bir yazma kilidi yoktur; akış aynı kurallarla yürür.
5. **Kontrol:** Bağımsız kontrolcü her ölçütü kendi yöntemiyle denetler; rapor tablo hâlinde gösterilir.
6. **Kabul:** Rapor incelenir. Kabul için yalnızca `evet`, ret için yalnızca `hayır` yazılır. Karar `.aec/gunluk.md` dosyasına kaydedilir.

## Örnek akış: karmaşık iş

**İstek:** `Revit'te B blok zemin kata, aks ölçülerine göre dört iç kapı yerleştir. Kopya modelde çalış.`

1. **Sınıf:** Ajan işin karmaşık iş olarak yürütüleceğini bildirir: iş Revit modelini değiştirmektedir. Küçük bir değişiklik de bu sınıftadır; yalnızca belgeler kısa tutulur.
2. **Görüşme:** Görüşme konu konu ilerler: amaç, kapsam, kapsam dışı, mevcut durum ve kabul ölçütleri. Her konunun sonunda bir özet sunulur ve teyidiniz istenir. Seviyeler ve yüklü kapı aileleri modelden okunur; bunlar ayrıca sorulmaz. Kabul ölçütleri bu aşamada kesinleşir, örneğin:
   - Kapı sayısı, aile ve tipi plana uygundur (revit-okuma).
   - Yazılan model kopya modeldir (revit-okuma).
   - Kapı konumları plana tolerans içinde uyar (olcu; bugün DOĞRULANAMADI çıkabilir).
3. **Belgeler ve onay:** Tarif, plan ve görevler sırayla gösterilir. Her belge ayrı onaylanır: tarif → `evet` → plan → `evet` → görevler → `evet`. Bir belge onaylanmadan sonraki belgeye geçilmez.
4. **Uygulama:** Revit'e yazma ancak görevler onaylandıktan sonra açılır. Çalışma sırasında izin ekranı görüntülenirse yapılacak işlem onaylanan planla karşılaştırılır ([Güvenlik İlkeleri](GUVENLIK.md)).
5. **Kontrol:** Bağımsız kontrolcü ölçütleri modelden okuyarak denetler. Konum ölçütü DOĞRULANAMADI olarak raporlanırsa kapı konumlarının sizin tarafınızdan kontrol edilmesi gerekir.
6. **Kabul:** Kabul için yalnızca `evet`, ret için yalnızca `hayır` yazılır. Ret durumunda gerekçeniz sorulur ve plan düzeltilerek yeniden onaya sunulur.
7. **Kaydetme ve eşitleme:** Model, iş kabul edildikten sonra ve yalnızca istemeniz hâlinde kaydedilir. Merkez modelle eşitlemeyi siz yaparsınız.

## Revit modelleme

**Durum:** Revit bağlantısı kurulu bilgisayarlarda kullanılabilir (bağlantı durumu `/aec:kontrol-et` ile görüntülenebilir).

**Eksik istek:** `Duvarları çiz.`

**Önerilen istek:** `Revit'te Zemin kat'a, A blok planındaki ölçülerle iç duvarları kopya modelde oluştur.`

**Ön kapının sorabileceği bilgiler** (karmaşık iş; görüşmede ele alınır):

- kopya model mi
- kat/seviye
- aile ve tip
- ölçü kaynağı

## DWG okuma/aktarma

**Durum:** Yakında (Faz 1B). Şu aşamada ölçüler kullanıcı tarafından verilirse plan hazırlanabilir.

**Eksik istek:** `Şu çizimi Revit'e at.`

**Önerilen istek:** `A blok DWG dosyasındaki duvar ve kolon katmanlarını oku. Birim milimetre. Önce ne bulduğunu listele.`

**Ön kapının sorabileceği bilgiler** (en önemli üçü sorulur; çizimin Revit'e aktarılması karmaşık iş olarak yürütülür):

- hangi dosya ve pafta
- hangi katmanlar
- birim ve ölçek
- DWG–Revit hizası

## DWG'de çizim

**Durum:** Yakında.

**Eksik istek:** `Detay çiz.`

**Önerilen istek:** `Yeni bir DWG dosyasında, 1/20 ölçekte, kapı eşiği detayını çiz. Orijinal dosyaya dokunma.`

**Ön kapının sorabileceği bilgiler** (karmaşık iş; görüşmede ele alınır):

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

**Ön kapının sorabileceği bilgiler** (karmaşık iş; görüşmede ele alınır):

- hangi geometri
- Revit'te hangi kategori
- birim ve orijin

## Asma tavan

**Durum:** Yakında (Faz 1D).

**Eksik istek:** `Tavanı yap.`

**Önerilen istek:** `Zemin kat koridorunun asma tavanını DWG tavan planından kopya modelde oluştur.`

**Ön kapının sorabileceği bilgiler** (karmaşık iş; görüşmede ele alınır):

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
