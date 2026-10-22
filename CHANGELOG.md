# Değişiklik Günlüğü

## Yayınlanmamış (dev)

- İstek karşılama katmanı (ön kapı) eklendi: isteği tanır, eksik bilgileri sorar (en fazla 3 soru), plan sunar ve onay alındıktan sonra uygular.
- Yedi iş türü için iş kartları eklendi: Revit modelleme, DWG okuma/aktarma, DWG'de çizim, Metraj/liste, Rhino'dan Revit'e, Asma tavan, Render/görsel.
- Yeni komutlar eklendi: `/aec:kontrol-et`, `/aec:proje-baslat`, `/aec:yardim`.
- `kur.ps1` ve `kur.cmd` ile tek adımlı kurulum eklendi. İki kanal tanımlandı: `main` (tüm kullanıcılar) ve `dev` (pilot kullanıcılar).
- Kurulum, değişiklik yapmadan önce ayar dosyasını yedekler (`settings.json.aec-yedek`).
- Türkçe belgeler eklendi: kurulum ve ilk kullanım, örnek istekler, güvenlik ilkeleri, sorun giderme, sözlük.
- Ön kapı iyileştirildi: sorulardan sonra da taslak plan ve açık bir onay sorusu sunulur; "şu planı düzelt" gibi iş türü belirli olmayan kısa isteklerde de ön kapı devreye girer.
