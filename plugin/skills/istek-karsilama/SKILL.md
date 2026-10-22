---
name: istek-karsilama
description: Her Revit, AutoCAD/DWG/DXF, Rhino, metraj, tavan ya da render isteğinde işe başlamadan ÖNCE kullan. Kullanıcı kendi sözleriyle Revit'te duvar, kapı, kolon, aile ya da seviye işi, DWG'den ölçü okuma ya da Revit'e aktarma, AutoCAD'de çizim, detay çizme ya da DXF üretme, Rhino'dan Revit'e geçirme, metraj, alan hesabı, mahal ya da kapı/pencere listesi, Excel tablosu, asma tavan (baffle, bandraster, open cell, menfez) ya da render/görsel istediğinde doğru iş kartını yükler. Eksik bilgiyi proje MD'sinden doldurur, en fazla 3 soru sorar, planı VARSAYIM'larla gösterir, onay alır, uyguladıktan sonra geri okur.
---

# İstek karşılama (ön kapı)

Ofisteki arkadaşlar isteği kendi sözleriyle ve çoğu zaman eksik yazar. Tahminle yanlış bir şey üretmek
"yapay zekâ çalışmıyor" dedirtir. Bu skill işi tanır, eksiği yakalar, planı gösterir, onaydan sonra başlar.

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

İstek iki işe giriyorsa iki kartı da oku. Hiçbirine uymuyorsa bu skill'i bırak, normal çalış.

## Prosedür

1. **Kartı seç.** Bağlamda `[aec ön kapı]` kartı varsa onun söylediği kartı kullan. Yoksa isteği yukarıdaki
   tabloyla eşleştir.
2. **Kartı oku.** Kart dosyası bu skill'in klasöründeki `kartlar/` altında: `${CLAUDE_SKILL_DIR}/kartlar/<kart>.md`.
   Kartı okumadan plan yazma.
3. **Proje MD'sini oku.** Proje klasöründeki `CLAUDE.md` ve `.aec/proje.md` dosyaları. Yoksa bir cümleyle
   `/aec:proje-baslat`'ı öner ("projeyi bir kez tanıtırsanız bunları her seferinde sormam") ve işe devam et.
4. **Eksiği doldur.** Kartın "Kritik gerekenler" listesini önce proje MD'sinden, sonra açık model ya da çizimden
   araçla okuyarak doldur. Kalanlar için en fazla 3 soru sor; bütün soruları tek mesajda numaralı liste hâlinde
   sor, mümkünse seçenek ver. Sormadığın her şeyi planda VARSAYIM diye yaz.
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
