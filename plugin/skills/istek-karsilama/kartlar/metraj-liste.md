# Metraj/liste

## Tanıma
- Metraj, alan hesabı, hacim; mahal listesi; kapı, pencere ya da doğrama listesi; Excel tablosu.
- Kullanıcının sözleri: "mahal listesini çıkar", "kat kat m2 hesabı", "kapı listesini Excel'e dök".

## Kritik gerekenler
- kaynak Revit mi DWG mi: liste hangi dosyadan çıkacak (kopya model ya da çizim).
- net mi brüt mü: alanlar net mi, brüt mü; duvar içi ve şaftlar dahil mi.
- Excel biçimi: sütunlar, sıralama (kat, mahal no), ofis şablonu var mı.
- poz no (fiyatsız): poz numarası yazılır, birim fiyat ve tutar hiç yazılmaz.

## İkincil
- Birim: m², m³, m, adet; ondalık basamak.
- Kat ya da blok bazında ara toplamlar.
- Mahal adları ve numaraları modeldeki yazımla mı, ofis listesiyle mi.

## Proje MD'sinde nerede
- `.aec/proje.md`: proje tipi, birim, kat listesi, Revit kopya yolu.
- `CLAUDE.md`: projenin Excel ya da poz kuralları, varsa.
- Poz numaraları MD'de yoksa kullanıcıya sor ya da boş bırakıp sarıyla işaretle.

## Skill / araç
- Metraj modülü yakında; bu iş için özel araç henüz yok (yakında).
- Genel akış: görüşme → plan onayı → yeni dosyada uygula → kontrolcü → kabul.
- Revit kaynağı: araç listende adında `revit` geçen araç varsa oda, kapı, pencere bilgisini onunla oku.
- DWG kaynağı: DWG okuma araçları yakında (Faz 1B); ölçüyü resimden çıkarma. Ancak kod çalıştırabiliyorsan
  kişinin verdiği DXF'i `dwg-okuma` kartındaki gibi betikle oku ve değerleri "kontrol edin" diye işaretle.
- Excel'i yeni dosya olarak yaz (Excel skill'i ya da kod gerekir); ikisi de yoksa bunu söyle, tabloyu sohbette ver.
- Ofis renkleri: sarı `FFF2CC` = kontrol et, mavi `DDEBF7` = değişti.
- Bakanlık birim fiyatları kullanılmaz; fiyat ya da tutar sütunu ekleme.

## Plan şablonu
1. Kaynak: <kopya model ya da çizim>. Alan: <net/brüt>.
2. Liste: <mahal / kapı / pencere / alan>; sütunlar: <liste>.
3. Çıktı: <yeni Excel dosyası adı>; poz no sütunu, fiyat yok.
4. VARSAYIM: <sorulmayanlar>; emin olunmayan hücreler sarı.
5. Kabul ölçütleri: <ölçütler ve yöntemleri>.

## Kabul ölçütleri
Varsayılan ölçütlerdir; görüşmede işe göre kesinleştirilir ve `olcut` komutuyla kaydedilir.
- Excel plandaki yeni dosya adıyla oluşturulmuştur; satır sayısı kaynaktaki öğe sayısıyla aynıdır (dosya)
- Ara toplamlar ve genel toplam kaynaktaki değerlerle tutar (dosya)
- Tabloda birim fiyat, fiyat ya da tutar sütunu yoktur; poz no sütunu vardır (dosya)

## Geri okuma
- Excel'i yazdıktan sonra dosyayı yeniden aç: satır sayısı, toplamlar, boş hücreler.
- Toplamları kaynaktan ikinci kez okuyup karşılaştır (ör. Revit'teki oda alanları ile tablodaki toplam).
- Tutmayan satırları sarıyla işaretle ve kullanıcıya listele.

## Yapamıyorsam
- "Revit bağlantısı bu bilgisayarda kurulu olmadığından ya da Revit kapalı olduğundan liste modelden çıkarılamıyor. Bağlantı durumu /aec:kontrol-et komutuyla görüntülenebilir."
- "Liste (schedule) Revit'ten dışa aktarılıp dosya iletilirse tablo bu dosyadan hazırlanabilir."
- DWG kaynağında: "DWG okuma Faz 1B ile eklenecektir; alanlar görüntüden tahmin edilmez. Alan değerleri kullanıcı tarafından iletilirse planda VARSAYIM olarak işaretlenir." DXF yolunu yalnızca kod çalıştırabiliyorsan öner.
- Fiyat istenirse: "Ofis kuralı gereği tabloya birim fiyat ve tutar yazılmaz; yalnızca poz numaraları yazılır."
