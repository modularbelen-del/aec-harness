# Örnek istekler

İsteğinizi ne kadar açık yazarsanız o kadar az soru gelir. Her işte aynı sıra izlenir: en fazla 3 soru, sonra varsayımlarla birlikte plan, siz onaylayınca uygulama, en sonda geri okuma.

Varsayım, sormadığım ama doğru kabul ettiğim şeydir. Planda **VARSAYIM** diye işaretlenir. Yanlışsa düzeltin. ([Sözlük](SOZLUK.md))

Aşağıdaki isimler örnektir. Kendi proje ve kat adlarınızı yazın.

## Revit modelleme

**Böyle yazmayın:** `Duvarları çiz.`

**Böyle yazın:** `Revit'te Zemin kat'a, A blok planındaki ölçülerle iç duvarları kopya modelde oluştur.`

**Ön kapı şunu sorar:** Kopya model mi? Hangi kat? Hangi duvar tipi? Ölçüler nereden alınacak?

## DWG okuma/aktarma

**Böyle yazmayın:** `Şu çizimi Revit'e at.`

**Böyle yazın:** `A blok DWG dosyasındaki duvar ve kolon katmanlarını oku. Birim milimetre. Önce ne bulduğunu listele.`

**Ön kapı şunu sorar:** Hangi dosya ve pafta? Hangi katmanlar? Birim ve ölçek ne? Çizim ile Revit modeli aynı yerde mi duruyor?

## DWG'de çizim

**Böyle yazmayın:** `Detay çiz.`

**Böyle yazın:** `Yeni bir DWG dosyasında, 1/20 ölçekte, kapı eşiği detayını çiz. Orijinal dosyaya dokunma.`

**Ön kapı şunu sorar:** Yeni dosya mı, kopya mı? Hangi ölçek ve birim? Ölçüler nereden gelecek?

Not: AutoCAD bağlantısı henüz deneme aşamasındadır. Çalışmıyorsa size açıkça söylenir.

## Metraj/liste

**Böyle yazmayın:** `Metraj çıkar.`

**Böyle yazın:** `Zemin kat'taki odaların alanlarını mahal listesi olarak Excel tablosuna yaz. Birim metrekare.`

**Ön kapı şunu sorar:** Hangi kat veya bölüm? Hangi sütunlar? Hangi birim? Fiyat var mı? (Fiyat için Bakanlık birim fiyatları kullanılmaz.)

## Rhino'dan Revit'e

**Böyle yazmayın:** `Rhino'daki şeyi Revit'e geçir.`

**Böyle yazın:** `Rhino'daki cephe panellerini A blok Revit modelinin kopyasına aktar. Panel başına bir aile örneği olsun.`

**Ön kapı şunu sorar:** Hangi Rhino nesneleri? Revit'te hangi kategori? Hangi kat? Kopya model mi?

Not: Rhino bağlantısı henüz deneme aşamasındadır.

## Asma tavan

**Böyle yazmayın:** `Tavanı yap.`

**Böyle yazın:** `Zemin kat koridorunun asma tavanını DWG tavan planından kopya modelde oluştur. Armatür ve menfezleri çizimdeki yerlerine koy.`

**Ön kapı şunu sorar:** Hangi DWG ve hangi mahal? Tavan sistemi ve ölçüleri? Tavan yüksekliği? Tanımadığı bir işaret varsa ne olduğu?

## Render/görsel

**Böyle yazmayın:** `Güzel bir görsel yap.`

**Böyle yazın:** `A blok girişinin gündüz, insan gözü yüksekliğinde bir perspektif görselini hazırla.`

**Ön kapı şunu sorar:** Hangi görünüm veya kamera? Hangi ışık ve saat? Hangi boyut ve nereye kaydedilecek?

Not: Render henüz çalışmıyor. [Yakında](NELER-YAPABILIR.md) listesindedir.
