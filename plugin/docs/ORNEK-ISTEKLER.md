# Örnek istekler

İsteğinizi ne kadar açık yazarsanız o kadar az soru gelir. Her işte aynı sıra izlenir: en fazla 3 soru, sonra varsayımlarla birlikte plan, siz onaylayınca uygulama, en sonda geri okuma.

Varsayım, sormadığım ama doğru kabul ettiğim şeydir. Planda **VARSAYIM** diye işaretlenir. Yanlışsa düzeltin. ([Sözlük](SOZLUK.md))

Her başlığın altında önce o işin bugünkü durumu yazar. Aşağıdaki isimler örnektir. Kendi proje ve kat adlarınızı yazın.

"Ön kapı şunu sorar" altındaki listede o işte eksik olabilecek bilgiler var. Ön kapı bunların hepsini sormaz. Proje dosyanızdan ve açık modelden bulabildiğini kendisi doldurur, kalanlardan en önemli 3 tanesini sorar.

## Revit modelleme

**Durum:** Revit bağlantısı kurulu bilgisayarlarda çalışır (/aec:kontrol-et ile bakın).

**Böyle yazmayın:** `Duvarları çiz.`

**Böyle yazın:** `Revit'te Zemin kat'a, A blok planındaki ölçülerle iç duvarları kopya modelde oluştur.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- kopya model mi
- kat/seviye
- aile ve tip
- ölçü kaynağı

## DWG okuma/aktarma

**Durum:** yakında (Faz 1B); şimdilik ölçüleri siz verirseniz plan hazırlar.

**Böyle yazmayın:** `Şu çizimi Revit'e at.`

**Böyle yazın:** `A blok DWG dosyasındaki duvar ve kolon katmanlarını oku. Birim milimetre. Önce ne bulduğunu listele.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- hangi dosya ve pafta
- hangi katmanlar
- birim ve ölçek
- DWG–Revit hizası

## DWG'de çizim

**Durum:** yakında.

**Böyle yazmayın:** `Detay çiz.`

**Böyle yazın:** `Yeni bir DWG dosyasında, 1/20 ölçekte, kapı eşiği detayını çiz. Orijinal dosyaya dokunma.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- yeni dosya mı kopya mı
- katman standardı
- ölçek
- yazı stili

## Metraj/liste

**Durum:** Revit bağlıysa Revit'ten kısmen; DWG'den yakında.

**Böyle yazmayın:** `Metraj çıkar.`

**Böyle yazın:** `Zemin kat'taki odaların alanlarını mahal listesi olarak Excel tablosuna yaz. Birim metrekare.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- kaynak Revit mi DWG mi
- net mi brüt mü
- Excel biçimi
- poz no (fiyatsız)

## Rhino'dan Revit'e

**Durum:** yakında.

**Böyle yazmayın:** `Rhino'daki şeyi Revit'e geçir.`

**Böyle yazın:** `Rhino'daki cephe panellerini A blok Revit modelinin kopyasına aktar.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- hangi geometri
- Revit'te hangi kategori
- birim ve orijin

## Asma tavan

**Durum:** yakında (Faz 1D).

**Böyle yazmayın:** `Tavanı yap.`

**Böyle yazın:** `Zemin kat koridorunun asma tavanını DWG tavan planından kopya modelde oluştur.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- hangi DWG ve oda
- tavan sistemi
- kot
- kopya model mi

## Render/görsel

**Durum:** yakında; sahne tarifi ya da istem metni yazabilir.

**Böyle yazmayın:** `Güzel bir görsel yap.`

**Böyle yazın:** `A blok girişinin gündüz, insan gözü yüksekliğinde bir perspektif görseli için sahne tarifi yaz.`

**Ön kapı şunu sorar** (en önemli 3 tanesini):

- hangi görünüş
- stil
- gizlilik (müşteri çizimi)
