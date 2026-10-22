---
name: kontrol-et
description: Kullanıcı bir şeyin çalışmadığını söylediğinde ya da /aec:kontrol-et dediğinde kurulumu ve Revit, AutoCAD, Rhino bağlantılarını kontrol edip Türkçe bir tabloyla raporlar.
---

# Kurulum kontrolü

Yalnızca okuma yapılır. Hiçbir şey kaydedilmez, senkronlanmaz, değiştirilmez; Revit'te kod çalıştırılmaz.

1. Bash ile şunu çalıştır: `uv run --no-project python "<bu skill'in klasörü>/../../scripts/kontrol.py" --proje "<proje klasörü>"`.
   Çıktıdaki her satır "✓" ya da "✗" ile başlar. `uv` yoksa uv satırını kendin "✗ uv: kurulu değil → kur.cmd'yi çalıştırın (BASLA.md)" diye yaz.
2. Araç listende adında `revit`, `autocad` ya da `rhino` geçen MCP araçlarını say; her program için "bağlantı var / yok" yaz.
   Revit araçları varsa `get_revit_status`'u çağır ve sonucu göster. Başka bir şey çağırma.
3. `claude` komutu varsa `claude plugin list` çıktısındaki `aec` satırını "Plugin sürümü" olarak göster.
   Yoksa (Cowork) bu satıra "Customize > Plugins'te bakın" yaz.
4. Hepsini tek bir Türkçe tabloda ver (madde, durum, ne yapmalı). Her "✗" satırında kullanıcının ne yapacağını
   açıkça söyle. Teknik jargon kullanma.
