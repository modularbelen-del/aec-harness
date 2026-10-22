# Rhino'dan Revit'e

## Tanıma
- Rhino ya da Grasshopper'daki geometriyi Revit'e geçirme: cephe, panel, eğrisel duvar, çatı, özel form.
- Kullanıcının sözleri: "Rhino'daki cepheyi Revit'e geçir", "Grasshopper'dan Revit'e aktar", "3dm'yi modele al".

## Kritik gerekenler
- hangi geometri: hangi Rhino dosyası, katman ya da obje; yüzey mi, kapalı hacim mi, mesh mi.
- Revit'te hangi kategori: duvar, döşeme, çatı, cephe paneli ya da genel model.
- birim ve orijin: Rhino birimi (mm, m) ve Revit'le ortak nokta.

## İkincil
- Revit'in kendi elemanı mı (düzenlenebilir duvar, döşeme) yoksa sabit şekil mi (DirectShape).
- Aktarılacak bilgiler: ad, malzeme, panel numarası gibi parametreler.
- Kaç parça; parça sayısı çoksa önce küçük bir deneme.

## Proje MD'sinde nerede
- `.aec/proje.md`: birim, orijin ve koordinat, Revit kopya yolu.
- `CLAUDE.md`: projenin Rhino dosyası ve katman düzeni, varsa.

## Skill / araç
- Hedef yöntem: Rhino.Inside.Revit üzerine kod (Grasshopper içinde çalışan bileşen ya da betik).
- Bu iş için özel araç henüz yok (yakında); Rhino.Inside.Revit kodu için ayrı bir modül planlanıyor.
- Rhino.Inside.Revit bu bilgisayarda kurulu olmayabilir; Revit 2027 desteği de henüz doğrulanmadı. Kurulu
  olup olmadığını kişiye sor: Revit'te üstte "Rhinoceros" sekmesi görünüyor mu?
- Ofiste Rhino 8 var. Araç listende adında `rhino` geçen araç yoksa Rhino'ya bağlı değilsin.
- Kodu sen çalıştıramıyorsan kişinin Grasshopper'da çalıştıracağı kodu yaz; çalıştırmadığın şeyi "yaptım" deme.
- Genel prosedür: ölç → planla → onay al → kopya modelde uygula → geri oku.

## Plan şablonu
1. Kaynak: <Rhino dosyası, katman/obje>. Hedef: <kopya model>, kategori <kategori>.
2. Yöntem: Rhino.Inside.Revit üzerinden kod; Revit elemanı mı sabit şekil mi.
3. Birim ve hiza: <birim>, <ortak nokta>.
4. Önce <n> parçalık deneme, sonra hepsi.
5. VARSAYIM: <sorulmayanlar>. Onaylıyor musunuz?

## Geri okuma
- Revit'ten geri oku: öğe sayısı, kategori, kutu ölçüleri ve konum.
- Rhino'daki sayı ve ölçülerle karşılaştır; farkları tabloda göster.

## Yapamıyorsam
- "Rhino'dan Revit'e geçişi Rhino.Inside.Revit üzerinden kodla yapmayı hedefliyoruz. Bu bilgisayarda kurulu görünmüyor ya da Revit 2027 ile çalıştığı henüz doğrulanmadı; bu yüzden doğrudan aktaramıyorum."
- "Kuruluysa sizin Grasshopper'da çalıştıracağınız kodu adım adım yazabilirim. Durumu /aec:kontrol-et ile görebilirsiniz."
