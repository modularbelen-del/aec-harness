# Render/görsel

## Tanıma
- Render, görsel, perspektif, atmosfer görseli; Enscape, Lumion ya da Midjourney ile görsel üretme.
- Kullanıcının sözleri: "bu cepheden akşam render'ı", "lobiye atmosfer görseli", "perspektif çıkar".

## Kritik gerekenler
- hangi görünüş: hangi kamera, cephe ya da iç mekân; günün saati.
- stil: gerçekçi mi, eskiz gibi mi; malzeme ve ışık tarifi.
- gizlilik (müşteri çizimi): müşteri çizimi ya da model görüntüsü ücretsiz yapay zekâ sitelerine yüklenmez.

## İkincil
- Görselin nerede kullanılacağı (sunum, yarışma, müşteri toplantısı) ve oranı (yatay, dikey).
- Örnek alınacak referans görsel, kişinin kendi arşivinden.
- İnsan, araç, bitki gibi ekler.

## Proje MD'sinde nerede
- `CLAUDE.md`: projenin malzeme ve renk kararları, varsa.
- `.aec/proje.md`: yalnızca proje tipi (konut, ofis...); proje ve müşteri adı metne yazılmaz.

## Skill / araç
- Render modülü yakında; bu iş için özel araç henüz yok (yakında).
- Claude kendisi görsel üretmez; görsel ürettiğini ya da üreteceğini söyleme.
- Bugün yapılabilen: bir tarif yazmak. Enscape ya da Lumion'da yazı kutusu yoktur; tarif, sahneyi o render
  programında kurmanın adımlarıdır (kamera, saat, malzeme, ışık). Ofisin kullandığı bir görsel aracı varsa
  tarif, ona yazılacak istek metni de olabilir.
- Müşteri çizimini ya da model görüntüsünü ücretsiz yapay zekâ sitelerine yüklemeyi hiç önerme.
- Genel akış burada kısa: ihtiyacı topla → metni planla → plan onayı → metni dosyaya yaz ve ver → kontrolcü → kabul.

## Plan şablonu
1. Görünüş: <kamera ya da cephe>, saat <saat>.
2. Stil: <gerçekçi/eskiz>, malzeme ve ışık: <tarif>.
3. Çıktı: <render programında sahne tarifi / görsel aracına yazılacak metin>, <dosya adı> dosyasına yazılır;
   görseli kişi üretir.
4. Gizlilik: metinde proje ve müşteri adı yok.
5. VARSAYIM: <sorulmayanlar>. Kabul ölçütleri: <ölçütler ve yöntemleri>.

## Kabul ölçütleri
Varsayılan ölçütlerdir; görüşmede işe göre kesinleştirilir ve `olcut` komutuyla kaydedilir.
- Metin istenen görünüş, stil, malzeme ve ışık maddelerinin hepsini içerir (dosya)
- İstem metninde proje adı, müşteri adı ve adres geçmez (dosya)
- Kişi ürettiği görseli istekle karşılaştırarak gözle kontrol eder (kisi-gorsel)

## Geri okuma
- Yazdığın metni istekle karşılaştır: görünüş, stil, malzeme, ışık maddeleri tek tek var mı.
- Metinde proje ya da müşteri adı ve adres kalmadığını kontrol et.
- Kişi ürettiği görseli paylaşırsa istekle karşılaştırıp neyin tutmadığını söyle; görselden ölçü çıkarma.

## Yapamıyorsam
- "Render ve görsel üretimi özelliği yakında eklenecektir. Şu aşamada görsel üretilemiyor."
- "Bu süreçte, render programında sahnenin kurulması için bir tarif ya da ofisin kullandığı görsel aracına yazılacak bir istem metni hazırlanabilir."
- "Müşteri çizimleri ücretsiz yapay zekâ sitelerine yüklenmemelidir; bu sitelere yüklenen çizimler üçüncü kişilerin erişimine açılabilir."
