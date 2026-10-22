# DWG'de çizim

## Tanıma
Dört ayrı iş var; hangisi olduğunu baştan ayır:
1. Açık AutoCAD'de çizdirme: "AutoCAD'de şu planı çiz".
2. DWG/DXF dosyası üretme: "bunu DXF olarak hazırla".
3. Mevcut çizimi düzeltme: "şu paftadaki katmanları/ölçüleri düzelt".
4. Detay çizme: "parapet detayını 1/10 çiz".

## Kritik gerekenler
- yeni dosya mı kopya mı: yazma yalnızca yeni ya da kopya çizimde yapılır; orijinal DWG'ye hiç yazılmaz.
- katman standardı: ofis standardı mı, projenin kendi katmanları mı.
- ölçek: çizim ve yazdırma ölçeği (ör. 1/50, 1/10, 1/5).
- yazı stili: yazı tipi ve yüksekliği, ölçü stili.

## İkincil
- Birim (cm/mm) ve başlangıç noktası.
- Detayda malzeme katmanları, kalınlıklar, tarama.
- Pafta antedi ve çerçeve gerekiyor mu.

## Proje MD'sinde nerede
- `.aec/proje.md`: katman standardı, birim, orijin.
- `CLAUDE.md`: projenin yazı, ölçek ve pafta kuralları.

## Skill / araç
- Bu iş için özel araç henüz yok (yakında). AutoCAD bağlantısı değerlendiriliyor.
- Bu iş karmaşıktır (çizim). Akış: görüşme → tarif, plan ve görevler onayı → yeni ya da kopya dosyada uygula →
  kontrolcü → kabul.
- Araç listende adında `autocad` geçen bir araç varsa kullan. Yoksa AutoCAD henüz bağlı değil; açık AutoCAD'e
  çizdiğini hiç söyleme.
- DXF üretme ve kopya DXF'i düzeltme: yalnızca bu oturumda kod çalıştırabiliyorsan (Bash ve Python) yeni dosyaya yaz.
- Mevcut DWG'yi düzeltme: kopyasını iste ya da onaydan sonra kopyala; orijinalin üzerine hiç kaydetme.
- Ölçüler araçla ya da kullanıcıdan alınır; resimden ölçü alınmaz.

## Plan şablonu
1. İş: <dört işten hangisi>. Dosya: <yeni dosya adı ya da kopya yolu>.
2. Katmanlar: <standart>. Ölçek: <1/..>. Yazı: <stil, yükseklik>.
3. Çizilecekler: <öğe listesi ve ölçüler, kaynağıyla>.
4. VARSAYIM: <sorulmayanlar>.
5. Kabul ölçütleri: <ölçütler ve yöntemleri>.

## Kabul ölçütleri
Varsayılan ölçütlerdir; görüşmede işe göre kesinleştirilir ve `olcut` komutuyla kaydedilir.
- Çıktı, plandaki yeni ya da kopya dosya yolundadır; orijinal çizimin yolu kullanılmamıştır (dosya)
- Katman adları ve öğe sayıları plana uygundur (dosya)
- Ana ölçüler plandaki değerlerle tolerans içinde tutar (olcu; Faz 1C öncesinde DOĞRULANAMADI olabilir)

## Geri okuma
- Yazılan dosyayı yeniden aç ve oku: katman adları, öğe sayısı, ana ölçüler, yazılar.
- Plandaki ölçülerle karşılaştır; tutmayanı tabloda göster.

## Yapamıyorsam
- Araç listende `autocad` aracı yoksa: "AutoCAD bağlantısı henüz kurulu olmadığından açık AutoCAD oturumunda çizim yapılamıyor. Bağlantı durumu /aec:kontrol-et komutuyla görüntülenebilir."
- Kod çalıştırabiliyorsan: "Talep edilirse aynı çizim yeni bir DXF dosyası olarak hazırlanabilir; dosya AutoCAD'de açılarak DWG olarak kaydedilebilir."
- "Orijinal çizimde değişiklik yapılmaz; düzeltmeler dosyanın bir kopyası üzerinde yapılır."
