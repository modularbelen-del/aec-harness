# Karmaşık iş kuralı (aec)

Bu kural sabittir. İşin sınıfı kişiye sorulmaz; bu kurala göre belirlenir ve kişiye gerekçesiyle bir cümleyle bildirilir.

**Karmaşık iş:** Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren her iş karmaşıktır:
eleman ekleme, silme ya da değiştirme, çizim, detay, aile, başka programdan aktarma.

**Basit iş:** çizim programına yazmayan iştir: okuma, listeleme, kontrol, metraj ya da Excel raporu, soru-cevap,
render tarifi.

## Kart varsayılanları

| Kart | Varsayılan |
|---|---|
| revit-modelleme, dwg-cizim, rhino-revit, tavan | karmaşık |
| dwg-okuma, metraj-liste, render | basit |

İstek iki karta giriyorsa ve kartlardan biri karmaşıksa iş karmaşıktır.

## Yükseltme

Basit görünen iş planda çizim programına yazıyorsa onaydan önce karmaşık sınıfına yükseltilir ve kişiye gerekçesi
bildirilir. Örnek: DWG'den okunan duvarların Revit'e aktarılması.

Karmaşık iş, kişi istese de basit iş olarak yürütülmez; küçük bir işte belgeler kısa tutulur. Küçük bir Revit
düzeltmesi de (ör. bir kapının tipini değiştirme) karmaşık iştir.

## Sınıfın sonuçları

| Adım | Basit iş | Karmaşık iş |
|---|---|---|
| Görüşme | En fazla 3 soru, tek mesajda; kabul ölçütleri teklif edilir | Tam görüşme (`gorusme.md`); 3 soru sınırı uygulanmaz |
| Belgeler | Plan | Tarif, plan ve görevler |
| Onay | Plan için bir onay | Her belge için ayrı onay |
| Kontrol ve kabul | Bağımsız kontrolcü ve kişinin kabulü | Aynı |
