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
- Bu iş için özel araç henüz yok (yakında). AutoCAD bağlantısı henüz bağlı değil; değerlendiriliyor.
- Genel prosedürle çalış: ölç → planla → onay al → yeni ya da kopya dosyada uygula → geri oku.
- Araç listende adında `autocad` geçen bir araç varsa kullan; yoksa açık AutoCAD'e çizdiğini hiç söyleme.
- DXF üretme ve kopya DXF'i düzeltme: yalnızca bu oturumda kod çalıştırabiliyorsan (Bash ve Python) yeni dosyaya yaz.
- Mevcut DWG'yi düzeltme: kopyasını iste ya da onaydan sonra kopyala; orijinalin üzerine hiç kaydetme.
- Ölçüler araçla ya da kullanıcıdan alınır; resimden ölçü alınmaz.

## Plan şablonu
1. İş: <dört işten hangisi>. Dosya: <yeni dosya adı ya da kopya yolu>.
2. Katmanlar: <standart>. Ölçek: <1/..>. Yazı: <stil, yükseklik>.
3. Çizilecekler: <öğe listesi ve ölçüler, kaynağıyla>.
4. VARSAYIM: <sorulmayanlar>.
5. Onaylıyor musunuz?

## Geri okuma
- Yazılan dosyayı yeniden aç ve oku: katman adları, öğe sayısı, ana ölçüler, yazılar.
- Plandaki ölçülerle karşılaştır; tutmayanı tabloda göster.

## Yapamıyorsam
- "AutoCAD bağlantısı henüz bağlı değil, bu yüzden açık AutoCAD'inize çizemiyorum. Durumu /aec:kontrol-et ile görebilirsiniz."
- Kod çalıştırabiliyorsan: "İsterseniz aynı çizimi yeni bir DXF dosyası olarak hazırlarım; AutoCAD'de açıp DWG olarak kaydedersiniz."
- "Orijinal çizime dokunmam; düzeltme için dosyanın bir kopyasıyla çalışırım."
