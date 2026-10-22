# Revit modelleme

## Tanıma
- Revit'te duvar, döşeme, kolon, kiriş çizme; kapı ya da pencere yerleştirme; aile ya da tip değiştirme; seviye işi.
- Kullanıcının sözleri: "Revit'te 3. kata kapı koy", "şu duvarları modelle", "kolonları akslara yerleştir".

## Kritik gerekenler
- kopya model mi: hangi dosyaya yazılacak; merkez modele hiç yazılmaz.
- kat/seviye: hangi seviye; gerekiyorsa üst seviye ya da yükseklik.
- aile ve tip: projede yüklü hangi aile ve tip (araçla listelenir, tahmin edilmez).
- ölçü kaynağı: ölçüler nereden geliyor (DWG, kullanıcının yazdığı ölçü, mevcut model); görselden ölçü alınmaz.

## İkincil
- Birim (cm/mm) ve konum referansı: aks, mevcut duvar ya da proje orijini.
- Duvarın hangi yüzünden yerleşeceği (iç yüz, orta, dış yüz); kapının açılış yönü.
- Workset ve faz, projede kullanılıyorsa.

## Proje MD'sinde nerede
- `.aec/proje.md`: Revit merkez ve kopya yolu, birim, kat listesi, orijin.
- `CLAUDE.md`: "Revit'e yalnızca kopya modelde yaz" satırı ve projenin kendi kuralları.
- MD'de yoksa açık modelden oku: seviye listesi (`list_levels`), yüklü aileler (`list_families`).

## Skill / araç
- Bu iş için özel araç henüz yok (yakında). Bu iş karmaşıktır; akış: görüşme → tarif, plan ve görevler onayı →
  kopyada uygula → kontrolcü → kabul.
- Araç listende adında `revit` geçen araçlar var mı bak (ör. `revit` ya da `revit2` sunucusu: `get_revit_status`,
  `get_revit_model_info`, `get_current_view_info`, `list_levels`, `list_families`, `place_family`, `execute_revit_code`).
- Yazmadan önce açık belgenin dosya yolunu `get_revit_model_info` ile `.aec/proje.md`'deki kopya yoluyla karşılaştır;
  başlık yetmez. MD yoksa ya da yollar tutmuyorsa dur ve sor.
- `execute_revit_code` okuma için de olsa yazma sayılır: onaydan önce reddedilir, onaydan sonraki ilk başarılı çağrı
  işi `uygulandi` yapar. Okuma aracı yolu vermiyorsa uygulama kodu ilk iş olarak `Document.PathName`'i karşılaştırsın;
  tutmazsa hata fırlatıp hiçbir şey yazmadan dursun.
- Onaylı planın hepsini tek `execute_revit_code` çağrısında, tek TransactionGroup içinde (sonunda Assimilate) yapmaya
  çalış. Olmuyorsa (`place_family` çağrıları, sunucunun kendi işlemi) geri almanın birkaç adım sürebileceğini söyle.
- Ofiste Revit 2027 var. API'yi ezberden yazma; emin olmadığın sınıfı açık modelden doğrula.
- `save_document` ve `sync_with_central` araçlarını kendiliğinden çağırma; kaydetme ve eşitleme kişinin işi.

## Plan şablonu
1. Dosya: <kopya model yolu> (açık belgenin yolu proje MD'siyle karşılaştırıldı).
2. Seviye: <seviye>. Aile ve tip: <aile : tip>.
3. Yapılacak: <adet> <öğe>; konumlar <ölçü kaynağı>'ndan.
4. VARSAYIM: <sorulmayan her şey, ör. duvar ortasından yerleşim>.
5. <Tek seferde yazılamıyorsa:> Geri almak birkaç adım sürebilir.
6. Kabul ölçütleri: <ölçütler ve yöntemleri>; uygulamadan sonra bağımsız kontrolcü bunları modelden okur.

## Kabul ölçütleri
Varsayılan ölçütlerdir; görüşmede işe göre kesinleştirilir ve `olcut` komutuyla kaydedilir.
- Eleman sayısı, aile ve tipi plana uygundur (revit-okuma)
- Yazılan model kopya modeldir; açık belgenin yolu `.aec/proje.md`'deki kopya yoluyla aynıdır (revit-okuma)
- Konum ve ölçüler plana tolerans içinde uyar (olcu; Faz 1C öncesinde DOĞRULANAMADI olabilir)

## Geri okuma
- Yazdıktan sonra Revit okuma araçlarıyla oku: öğe sayısı, seviye, aile ve tip, konum ve ölçüler.
- Plandaki her maddeyle karşılaştır; tutmayanı tabloda göster.
- Kendi yazdığın kodun çıktısına bakıp "tamam" deme; sonucu modelden ayrıca oku.

## Yapamıyorsam
- "Revit bağlantısı bu bilgisayarda kurulu olmadığından ya da Revit kapalı olduğundan modelde işlem yapılamıyor. Bağlantı durumu /aec:kontrol-et komutuyla görüntülenebilir."
- Açık dosya kopya değilse: "Açık dosya kopya model değildir. Kopya model açıldığında işleme devam edilebilir."
- "Talep edilirse adımlar, kullanıcı tarafından uygulanacak şekilde yazılabilir; çalıştırılmayan bir işlem yapılmış olarak bildirilmez."
