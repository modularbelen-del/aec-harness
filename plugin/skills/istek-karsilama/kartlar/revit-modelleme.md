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
- Bu iş için özel araç henüz yok (yakında). Genel prosedürle çalış: ölç → planla → onay al → kopyada uygula → geri oku.
- Araç listende adında `revit` geçen araçlar var mı bak (ör. `revit` ya da `revit2` sunucusu: `get_revit_status`,
  `get_revit_model_info`, `get_current_view_info`, `list_levels`, `list_families`, `place_family`, `execute_revit_code`).
- Yazmadan önce `get_revit_status` ve `get_revit_model_info` ile açık belgenin kopya model olduğunu başlığından doğrula.
- Onaylı plan başına tek bir TransactionGroup kullan (sonunda Assimilate), yalnızca kopya modelde.
- Ofiste Revit 2027 var. API'yi ezberden yazma; emin olmadığın sınıfı açık modelden doğrula.
- `save_document` ve `sync_with_central` araçlarını kendiliğinden çağırma; kaydetme ve eşitleme kişinin işi.

## Plan şablonu
1. Dosya: <kopya model adı> (açık belgenin başlığıyla doğrulandı).
2. Seviye: <seviye>. Aile ve tip: <aile : tip>.
3. Yapılacak: <adet> <öğe>; konumlar <ölçü kaynağı>'ndan.
4. VARSAYIM: <sorulmayan her şey, ör. duvar ortasından yerleşim>.
5. Hepsi tek işlem olarak yazılır; beğenmezseniz tek geri al ile döner.
6. Sonunda modelden geri okuyup bu planla karşılaştırırım. Onaylıyor musunuz?

## Geri okuma
- Yazdıktan sonra aynı Revit aracıyla oku: öğe sayısı, seviye, aile ve tip, konum ve ölçüler.
- Plandaki her maddeyle karşılaştır; tutmayanı tabloda göster.
- Kendi yazdığın kodun çıktısına bakıp "tamam" deme; sonucu modelden ayrıca oku.

## Yapamıyorsam
- "Revit bağlantısı bu bilgisayarda kurulu değil ya da Revit kapalı, bu yüzden modele dokunamıyorum. Durumu /aec:kontrol-et ile görebilirsiniz."
- Açık dosya kopya değilse: "Açık dosya kopya model değil. Kopya modeli açarsanız oradan devam ederim."
- "İsterseniz adımları sizin uygulayacağınız şekilde yazarım; çalıştırmadığım bir şeyi yaptım demem."
