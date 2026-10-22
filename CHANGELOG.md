# Değişiklik Günlüğü

## Yayınlanmamış (dev)

- İstek karşılama katmanı (ön kapı) eklendi: isteği tanır, eksik bilgileri sorar (en fazla 3 soru), plan sunar ve onay alındıktan sonra uygular.
- Yedi iş türü için iş kartları eklendi: Revit modelleme, DWG okuma/aktarma, DWG'de çizim, Metraj/liste, Rhino'dan Revit'e, Asma tavan, Render/görsel.
- Yeni komutlar eklendi: `/aec:kontrol-et`, `/aec:proje-baslat`, `/aec:yardim`.
- `kur.ps1` ve `kur.cmd` ile tek adımlı kurulum eklendi. İki kanal tanımlandı: `main` (tüm kullanıcılar) ve `dev` (pilot kullanıcılar).
- Kurulum, değişiklik yapmadan önce ayar dosyasını yedekler (`settings.json.aec-yedek`).
- Türkçe belgeler eklendi: kurulum ve ilk kullanım, örnek istekler, güvenlik ilkeleri, sorun giderme, sözlük.
- Ön kapı iyileştirildi: sorulardan sonra da taslak plan ve açık bir onay sorusu sunulur; "şu planı düzelt" gibi iş türü belirli olmayan kısa isteklerde de ön kapı devreye girer.
- İş akışı eklendi: her iş görüşme, kabul ölçütleri, plan onayı, uygulama, bağımsız kontrol ve kabul adımlarından geçer.
- Karmaşık iş kuralı eklendi: Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren her iş karmaşıktır. Bu işlerde tam görüşme yapılır; tarif, plan ve görevler ayrı ayrı onaylanır. Basit işte en fazla 3 soru sorulur ve yalnızca plan onaylanır.
- Onay, ret ve kabul yalnızca kişinin kısa "evet" ya da "hayır" mesajından, kod tarafından kaydedilir. Soru, şart ya da ek açıklama içeren mesaj onay sayılmaz. İş kaydı aracında onay ya da kabul komutu bulunmaz.
- Revit yazma kilidi eklendi: onaylanmış plan olmadan Revit'e yazma reddedilir, merkez modelle eşitleme her zaman reddedilir, kaydetme yalnızca iş kabul edildikten sonra yapılabilir. Kancaların çalışmadığı oturumlarda Revit'e yazmadan önce izin ekranında onay istenebilir.
- Bağımsız ve salt okuyan kontrolcü (`aec:dogrulayici`) eklendi: kabul ölçütlerini GEÇTİ, KALDI ya da DOĞRULANAMADI olarak raporlar; rapor kod tarafından iş klasörüne kaydedilir. Ölçü doğrulaması Faz 1C ile eklenecektir.
- İş kayıtları `.aec/isler/` klasöründe, kabul ve ret kararları `.aec/gunluk.md` dosyasında tutulur. Yeni oturumun başında açık işler ajana bildirilir ve devam etmesi önerilir.
- Açık bir işe yeni oturumda devam etmek için iş kaydı aracına `devam` komutu eklendi. Komut işi yeni oturuma bağlar; önceki oturumda verilmiş plan onayı yeniden istenir. Kabulde reddedilen işler de açık iş olarak listelenir.
- Kabul ölçütü zorunlu hâle getirildi: ilk belge (basit işte plan, karmaşık işte tarif) en az bir kabul ölçütü kaydedilmeden onaya sunulamaz. Ölçütü bulunmayan bir işin kontrol sonucu DOĞRULANAMADI olarak kaydedilir.
- Ajan, uygulanan bir işi bağımsız kontrol yapmadan bırakıp durmak isterse bir kez uyarılır.
- Belgeler iş akışına göre güncellendi. `THIRD_PARTY_NOTICES.md` eklendi: superpowers ve spec-kit projelerinden uyarlanan bölümlerin MIT lisans metinleri.
