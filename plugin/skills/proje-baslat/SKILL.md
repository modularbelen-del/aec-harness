---
name: proje-baslat
description: Projeyi bir kez tanıtır; birkaç soru sorar, projenin CLAUDE.md bloğunu ve .aec/proje.md dosyasını yazar. Yalnızca kullanıcı /aec:proje-baslat dediğinde çalışır.
disable-model-invocation: true
---

# Proje başlatma

Amaç: ofis çalışanının her seferinde aynı şeyleri anlatmasına gerek kalmasın, ajan tahmin yürütmesin. Soruları bir kez sorarsın, iki dosya yazılır.

1. Tek bir numaralı listede en fazla 6 soru sor, hepsini aynı mesajda. Bilmediği soruyu boş bırakabileceğini söyle:
   1. Projenin adı ve tipi nedir (konut, ofis, otel gibi)?
   2. Revit merkez modelin ve kopya modelin yolu nedir? (Tek soru; yazmaya yalnızca kopyada izin verilir.)
   3. Çizim birimi nedir (mm, cm, m)?
   4. Katlar hangileri (örneğin B1, Z, 1-4)?
   5. Orijin nedir (proje temel noktası, ölçüm noktası ya da başka bir şey)?
   6. Katman standardı nedir (ofis standardı ya da başka)?
2. Cevapları şu anahtarlarla bir JSON nesnesine çevir: `proje_adi`, `proje_tipi`, `revit_merkez`, `revit_kopya`, `birim`, `katlar`, `orijin`, `katman_standardi`. Cevapsız alanı boş bırak ya da hiç yazma. Yalnızca bu alanları yaz; müşteriye ait kişisel bilgi (ad, telefon, adres, e-posta) sorma ve yazma.
3. Bash ile JSON'u stdin'den ver: `uv run --no-project python "<bu skill'in klasörü>/../../scripts/proje_baslat.py" --proje "<proje klasörü>" --json -`.
   Betik Türkçe sonuç satırları basar; bunları kullanıcıya aynen göster.
4. `uv` yoksa dosyaları kendin yaz, aynı kurallarla (UTF-8, BOM'suz):
   - `.aec/proje.md`: her alan için `- **<etiket>:** <değer ya da "belirtilmedi">` satırı (etiketler: Proje adı, Proje tipi, Revit merkez model, Revit kopya model, Birim, Katlar, Orijin, Katman standardı). Dosya zaten varsa dokunma, "zaten var, değiştirilmedi" de.
   - `CLAUDE.md`: `<!-- aec:proje başlangıç -->` ve `<!-- aec:proje bitiş -->` işaretleri arasında üç satır: "Bu proje aec ile çalışır; proje bilgileri .aec/proje.md dosyasında.", "Revit'e yalnızca kopya modelde yaz: <kopya model>.", "Birim: <birim>.". İşaretler varsa bloğu yerinde değiştir, yoksa dosyanın sonuna bir boş satırla ekle. Kullanıcının diğer metnine dokunma.
5. Sonunda tek cümleyle neyin yazıldığını söyle.
