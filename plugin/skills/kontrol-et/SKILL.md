---
name: kontrol-et
description: Kullanıcı bir şeyin çalışmadığını söylediğinde ya da /aec:kontrol-et dediğinde kurulumu ve Revit, AutoCAD, Rhino bağlantılarını kontrol edip Türkçe bir tabloyla raporlar.
---

# Kurulum kontrolü

Yalnızca okuma yapılır. Hiçbir şey kaydedilmez, senkronlanmaz, değiştirilmez; Revit'te kod çalıştırılmaz.

1. Bash ile şunu çalıştır: `uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/kontrol.py" --proje "${CLAUDE_PROJECT_DIR}"`.
   Çıktıdaki her satır "✓" ya da "✗" ile başlar. `uv` yoksa uv satırını kendin "✗ uv: kurulu değil → BASLA.md'deki tek satırlık kurulum komutunu yeniden çalıştırınız" diye yaz ve diğer satırları elle üret:
   proje klasöründe `CLAUDE.md` ve `.aec/proje.md` var mı diye dosya kontrolüyle bak (yoksa "bulunamadı → /aec:proje-baslat");
   otomatik güncelleme için "durumu belirlenemedi → /plugin > Marketplaces ya da Cowork'te Customize > Plugins" yaz.
2. Araç listende adında `revit`, `autocad` ya da `rhino` geçen MCP araçlarına bak. Bir program ancak aracı listede
   VARSA ve zararsız bir okuma/durum çağrısı yanıt verirse "bağlı" yazılır. Revit için `get_revit_status`'u çağır.
   AutoCAD ve Rhino için zararsız bir durum/okuma aracı varsa onu çağır. Böyle bir araç yoksa ya da çağrı hata verirse
   ya da boş dönerse "araç mevcut, yanıt doğrulanamadı → programı açarak kontrolü yineleyiniz" yaz. Hiç araç yoksa
   "bu bilgisayarda kurulu değil → ofisteki sistem sorumlusuna bildiriniz" yaz (AutoCAD ve Rhino için
   "bağlantı desteği yakında eklenecektir" diye ekle). Başka bir şey çağırma.
   Betiğin "Açık programlar" satırı yalnızca bir ipucudur; onu asla "bağlı" diye tekrarlama.
3. `claude` komutu varsa `claude plugin list` çıktısındaki `aec` satırını "Plugin sürümü" olarak göster.
   Yoksa (Cowork) bu satıra "Customize > Plugins bölümünden görüntülenebilir" yaz.
4. Hepsini tek bir Türkçe tabloda ver (madde, durum, ne yapmalı). Her "✗" satırında kullanıcının ne yapacağını
   açıkça söyle. Teknik jargon kullanma.
