# Asma tavan

## Tanıma
- Asma tavan, alın (kapama), baffle, bandraster, open cell, delikli panel, menfez, lineer armatür, LED panel.
- Kullanıcının sözleri: "tavanı DWG'den çıkar", "koridora baffle tavan yap", "armatürler kenara ulaşmıyor, düzelt".

## Kritik gerekenler
- hangi DWG ve oda: tavan planı hangi dosyada, hangi odalar.
- tavan sistemi: sistem ve ürün (ör. 60x60 panel, baffle aralığı, open cell gözü).
- kot: tavan yüksekliği ve alın yükseklikleri; hangi seviyeden ölçülüyor.
- kopya model mi: tavan yalnızca kopya modelde kurulur.

## İkincil
- Aydınlatma ve menfez yerleri, modül başlangıcı (aks ya da oda ortası).
- Kenar boşlukları, duvar dibi profili, askı.
- Çizimde tanınmayan blok ya da ürün kodu (ör. bir notta geçen kod).

## Proje MD'sinde nerede
- `.aec/proje.md`: Revit kopya yolu, birim, kat listesi, orijin.
- `CLAUDE.md`: projenin tavan tipleri ve kuralları, varsa.

## Skill / araç
- Bu iş karmaşıktır; iş kaydı, tarif, plan ve görevler onayı, kontrolcü ve kabul bu akışla yürür.
- Oturumda `ceiling-from-dwg` skill'i varsa görüşmede DWG'nin okuma ve çözümlemesi için kullanılabilir; uygulama
  adımında onun prosedürüyle çalış. Bu skill'in yazma adımları (Revit'e yazma, dosya üretme) yine yalnızca onaylı
  planla yapılır.
- Tanınmayan tavan öğesi ya da ürün için oturumda `tavan-arastirma` skill'i varsa onu kullan.
- Bu skill'ler yoksa: tavan modülü yakında (Faz 1D). Özel araç henüz yok (yakında); genel akışla çalış:
  görüşme → onaylar → kopya modelde uygula → kontrolcü → kabul.
- Ölçüler DWG'den araçla okunur; resimden ölçü alınmaz. Revit'e yazmak için `revit-modelleme` kartındaki kurallar geçerli.

## Plan şablonu
1. Çizim ve odalar: <dosya>, <oda listesi>.
2. Sistem: <sistem, ürün>. Kot: <yükseklik>, seviye <seviye>.
3. Model: <kopya model>; aydınlatma ve menfezler <var/yok>.
4. VARSAYIM: <sorulmayanlar>.
5. Kabul ölçütleri: <ölçütler ve yöntemleri>.

## Kabul ölçütleri
Varsayılan ölçütlerdir; görüşmede işe göre kesinleştirilir ve `olcut` komutuyla kaydedilir.
- Tavan, armatür ve menfez sayıları ve tipleri plana uygundur (revit-okuma)
- Yazılan model kopya modeldir; açık belgenin yolu `.aec/proje.md`'deki kopya yoluyla aynıdır (revit-okuma)
- Kot ve tavan sınırları plana tolerans içinde uyar (olcu; Faz 1C öncesinde DOĞRULANAMADI olabilir)
- Boşluk kalmadığı, armatürlerin kenara ulaştığı ve alın köşelerinin kapalı olduğu gözle kontrol edilir (kisi-gorsel)

## Geri okuma
- Revit'ten geri oku: tavan sayısı, kot, sınırlar; armatür ve menfez sayısı.
- DWG'deki sınır ve adetlerle karşılaştır: boşluk kalmış mı, armatür kenara ulaşıyor mu, alın köşeleri kapalı mı.
- Tutmayanı oda oda tabloda göster.

## Yapamıyorsam
- "Tavan modülü yakında eklenecektir (Faz 1D). Bu bilgisayarda tavan aracı yüklü olmadığından tavan çizimden otomatik olarak oluşturulamıyor."
- "Revit bağlantısı bulunmadığında modele yazma yapılamaz. Bağlantı durumu /aec:kontrol-et komutuyla görüntülenebilir."
- "Bu süreçte odalar, tavan sistemi ve kotlar bir plan hâlinde hazırlanabilir; plan, araç kullanıma sunulduğunda uygulanmaya hazır olur."
