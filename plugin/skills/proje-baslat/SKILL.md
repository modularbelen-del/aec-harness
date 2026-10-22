---
name: proje-baslat
description: Projeyi bir kez tanıtır; birkaç soru sorar, projenin CLAUDE.md bloğunu ve .aec/proje.md dosyasını yazar. Yalnızca kullanıcı /aec:proje-baslat dediğinde çalışır.
disable-model-invocation: true
---

# Proje başlatma

Amaç: ofis çalışanının her seferinde aynı şeyleri anlatmasına gerek kalmasın, ajan tahmin yürütmesin. Soruları bir kez sorarsın, iki dosya yazılır.

Hedef klasör: `${CLAUDE_PROJECT_DIR}` (Claude'un açıldığı proje klasörü). Dosyalar yalnızca buraya yazılır.
Hedef klasör kişinin kendi kullanıcı (ev) klasörü ya da bir sürücünün kökü ise soru sorma, hiçbir şey yazma;
"Claude bir proje klasöründe açılmamıştır. Claude'u projenin klasöründe açarak /aec:proje-baslat komutunu yeniden çalıştırınız." de ve dur.

1. Tek bir mesaj yaz. Önce hedef klasörü söyle: "Proje bilgileri şu klasöre yazılacaktır: ${CLAUDE_PROJECT_DIR}. Klasör
   hatalıysa lütfen belirtiniz." Sonra tek bir numaralı listede en fazla 6 soru sor, hepsini aynı mesajda. Bilmediği soruyu boş
   bırakabileceğini söyle:
   1. Projenin adı ve tipi nedir (konut, ofis, otel gibi)?
   2. Revit merkez modelin ve kopya modelin dosya yolu nedir? (Tek soru; yazma işlemine yalnızca kopya modelde izin verilir.)
   3. Çizim birimi nedir (mm, cm, m)?
   4. Katlar hangileridir (örneğin B1, Z, 1-4)?
   5. Orijin nedir (proje temel noktası, ölçüm noktası ya da başka bir nokta)?
   6. Katman standardı nedir (ofis standardı ya da başka bir standart)?
2. Cevapları şu anahtarlarla bir JSON nesnesine çevir: `proje_adi`, `proje_tipi`, `revit_merkez`, `revit_kopya`, `birim`, `katlar`, `orijin`, `katman_standardi`. Cevapsız alanı boş bırak ya da hiç yazma. Yalnızca bu alanları yaz; müşteriye ait kişisel bilgi (ad, telefon, adres, e-posta) sorma ve yazma.
3. Bash ile JSON'u stdin'den ver: `uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/proje_baslat.py" --proje "${CLAUDE_PROJECT_DIR}" --json -`.
   Betik Türkçe sonuç satırları basar; bunları kullanıcıya aynen göster. Betik kullanıcı klasörüne ve sürücü köküne
   yazmaz; "Hiçbir şey yazılmadı" derse başka yere yazmaya çalışma, betiğin söylediğini aktar.
4. `uv` yoksa dosyaları kendin yaz, aynı kurallarla (UTF-8, BOM'suz; kullanıcı klasörüne ya da sürücü köküne asla):
   - `.aec/proje.md`: her alan için `- **<etiket>:** <değer ya da "belirtilmedi">` satırı (etiketler: Proje adı, Proje tipi, Revit merkez model, Revit kopya model, Birim, Katlar, Orijin, Katman standardı). Dosya zaten varsa dokunma, "zaten var, değiştirilmedi" de.
   - `CLAUDE.md`: `<!-- aec:proje başlangıç -->` ve `<!-- aec:proje bitiş -->` işaretleri arasında üç satır: "Bu proje aec ile çalışır; proje bilgileri .aec/proje.md dosyasında.", "Revit'e yalnızca kopya modelde yaz: <kopya model>.", "Birim: <birim>.". İşaretler varsa bloğu yerinde değiştir, yoksa dosyanın sonuna bir boş satırla ekle. Kullanıcının diğer metnine dokunma.
5. Sonunda tek cümleyle neyin yazıldığını söyle.
