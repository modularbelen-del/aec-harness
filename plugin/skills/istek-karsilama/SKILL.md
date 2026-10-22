---
name: istek-karsilama
description: Her Revit, AutoCAD/DWG/DXF, Rhino, metraj, tavan ya da render isteğinde işe başlamadan ÖNCE kullan. Kullanıcı kendi sözleriyle Revit'te duvar, kapı, kolon, aile ya da seviye işi, DWG'den ölçü okuma ya da Revit'e aktarma, AutoCAD'de çizim, detay çizme ya da DXF üretme, Rhino'dan Revit'e geçirme, metraj, alan hesabı, mahal ya da kapı/pencere listesi, Excel tablosu, asma tavan (baffle, bandraster, open cell, menfez) ya da render/görsel istediğinde doğru iş kartını yükler. Hangi iş olduğu belli olmayan kısa ofis isteklerinde ("şu planı düzelt") de kullan. Eksik bilgiyi proje MD'sinden doldurur, en fazla 3 soru sorar, planı VARSAYIM'larla gösterir, onay alır, uyguladıktan sonra geri okur.
---

# İstek karşılama (ön kapı)

İstekler gündelik dille ve çoğu zaman bazı bilgiler eksik olarak gelir; bu doğaldır. Tahminle yanlış bir şey
üretmek güveni zedeler. Bu skill işi tanır, eksiği yakalar, planı gösterir, onaydan sonra başlar.

Ofisin döngüsü: ölç (görselden tahmin etme) → planla → onay al → kopya dosyada uygula → geri oku → doğrula.

## Kart tablosu

| Kart | Ne zaman |
|---|---|
| `revit-modelleme` | Revit'te duvar, döşeme, kolon, kiriş, kapı/pencere yerleştirme, aile, seviye, "modelle" |
| `dwg-okuma` | DWG/DXF'ten ölçü, katman, blok okuma; çizimden Revit'e aktarma |
| `dwg-cizim` | AutoCAD'de çizim, DWG/DXF üretme, mevcut çizimi düzeltme, detay çizme |
| `metraj-liste` | Metraj, alan hesabı, mahal listesi, kapı/pencere/doğrama listesi, Excel tablosu |
| `rhino-revit` | Rhino ya da Grasshopper geometrisini Revit'e geçirme |
| `tavan` | Asma tavan, baffle, bandraster, open cell, menfez, lineer armatür, LED panel |
| `render` | Render, görsel, perspektif, atmosfer |

İstek iki işe giriyorsa iki kartı da oku. Ofis işi değilse bu skill'i bırak, normal çalış.

İş türü belli değilse ama işin ofis çalışması olduğu belliyse (ör. "şu planı düzelt", "şunu hazırla": hangi dosya,
hangi program, neyin düzeltileceği yok) skill'i bırakma. Kart seçme; dosyayı, programı ve neyin düzeltileceğini
en fazla 3 soruyla sor, ardından 4. adımdaki gibi taslak plan ve onay sorusuyla bitir.

## Prosedür

1. **Kartı seç.** Bağlamda `[aec ön kapı]` kartı varsa onun söylediği kartı kullan. Ön kapı yalnızca kelimelere
   bakar; önerdiği kart istekle açıkça uymuyorsa (ör. "A blok" yazısı yüzünden DWG kartı geldiyse) körü körüne
   izleme, isteği yukarıdaki tabloyla yeniden eşleştir. Kart yoksa isteği tabloyla eşleştir.
2. **Kartı oku.** Kart dosyası bu skill'in klasöründeki `kartlar/` altında: `${CLAUDE_SKILL_DIR}/kartlar/<kart>.md`.
   Kartı okumadan plan yazma. Kartı okur okumaz, soru sormadan önce, gereken aracın bu oturumda olup olmadığına
   bak; yoksa 6. adımdaki "Yapamıyorsam" metnini hemen söyle.
3. **Proje MD'sini oku.** Proje klasöründeki `CLAUDE.md` ve `.aec/proje.md` dosyaları. Yoksa bir cümleyle
   `/aec:proje-baslat`'ı öner ("Proje bilgileri /aec:proje-baslat ile bir kez kaydedilirse bu bilgiler her istekte
   yeniden sorulmaz.") ve işe devam et.
4. **Eksiği doldur.** Kartın "Kritik gerekenler" listesini önce proje MD'sinden, sonra açık model ya da çizimden
   araçla okuyarak doldur. Kalanlar için en fazla 3 soru sor; bütün soruları tek mesajda numaralı liste hâlinde
   sor, mümkünse seçenek ver. Sormadığın her şeyi planda VARSAYIM diye yaz.
   Soruların altına planı VARSAYIM'larıyla taslak olarak da ekle ve mesajı açık bir onay sorusuyla bitir
   ("Bu varsayımlarla devam edilmesini onaylıyor musunuz?"). Soruya cevap beklemek, onay istemeyi ortadan kaldırmaz.
5. **Planı yaz, onay iste.** Planda adımlar, hangi kopya dosyada çalışılacağı ve VARSAYIM'lar olur. Kartın
   "Plan şablonu"nu kullan. Onay gelmeden hiçbir yazma aracını çağırma: dosya yazma, Revit'e yerleştirme,
   modeli değiştiren kod çalıştırma dahil. Okuma araçları serbest.
6. **Araç yoksa söyle.** Gereken araç bu oturumun araç listesinde yoksa kartın "Yapamıyorsam" metnini kullan ve
   `/aec:kontrol-et`'i öner. Tahminle sonuç üretme; çalıştırmadığın bir şeyi "yaptım" deme.
7. **Geri oku.** Uyguladıktan sonra kartın "Geri okuma" adımını yap. Sonucu plandaki maddelerle karşılaştırıp
   kısa bir tabloyla ver; tutmayan bir madde varsa açıkça söyle.

## Her işte

- Plan gösterildikten sonra gelen "evet", "tamam", "devam" gibi kısa bir cevap onaydır; yeni soru sorma.
- Orijinal dosyaya (merkez model, müşterinin DWG'si) yazma; yeni ya da kopya dosyada çalış.
- Kaydetme ve merkez modelle eşitleme işini kişi kendisi yapar. `save_document` ve `sync_with_central`
  araçlarını kendiliğinden çağırma.
- Ölçüyü ekran görüntüsünden çıkarma. Araçla oku ya da kullanıcıdan al; alamadığını VARSAYIM diye yaz.
- Kullanıcıya sade Türkçe ve onun kendi kelimeleriyle yaz; kısa maddeler kullan.
