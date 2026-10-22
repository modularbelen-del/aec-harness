# Neler yapabilir?

Bu eklenti henüz yolun başında. Aşağıda yalnızca bugün gerçekten çalışanlar var. Yakında olanları bugün çalışıyormuş gibi beklemeyin.

## Bugün çalışanlar

- **Ön kapı:** İsteğinizi tanıyıp önce plan gösteren karşılama. Yedi iş türünü tanır: Revit modelleme, DWG okuma/aktarma, DWG'de çizim, Metraj/liste, Rhino'dan Revit'e, Asma tavan, Render/görsel. En fazla 3 soru sorar, varsayımlarını açıkça yazar. Siz onaylamadan bir şey değiştirmeyecek şekilde ayarlandı; yine de izin ekranını okuyun ([Güvenlik](GUVENLIK.md)). Cowork'te karşılama kartı bazen gelmeyebilir; eklenti çoğu zaman yine çalışır, çalışmazsa `/aec:kontrol-et` yazın.
- **`/aec:kontrol-et`:** Kurulumun ve Revit, AutoCAD, Rhino bağlantılarının sağlam olup olmadığına bakar; sorun varsa ne yapacağınızı söyler.
- **`/aec:proje-baslat`:** Projeyi bir kez tanıtırsınız (birkaç soru); ajan proje bilgisini bu dosyadan okur, her seferinde yeniden sormaz.
- **`/aec:yardim`:** Bu sayfayı gösterir.
- **Güvenlik kuralları:** Eklenti orijinal dosyaya yazmayacak ve eşitlemeyi size bırakacak şekilde ayarlandı. Ayrıntı: [Güvenlik](GUVENLIK.md).

Revit: bugün temel Revit bağlantısı (Revit'in durumunu ve seviyeleri okuma, aileleri listeleme, onaydan sonra yerleştirme) yalnızca ofisin bu bağlantıyı kurduğu bilgisayarlarda çalışır. Yakında gelecek Revit köprüsü (Faz 1C) bunun üstüne, onaylı planı uygulayıp sonucu Revit'ten geri okuyarak kontrol eden hazır aracı ekleyecek. AutoCAD ve Rhino bağlantıları yakında.

Nasıl yazacağınızı [örnek isteklerde](ORNEK-ISTEKLER.md) görün. Kurulum için [Başlayın](BASLA.md).

## Yakında

Bunlar henüz çalışmıyor; tarih verilmiyor.

- DWG dosyasından okuma (Faz 1B)
- Revit köprüsü (Faz 1C): onaylı planı uygulayıp Revit'ten geri okuyarak doğrulayan araç (bugünkü temel bağlantının üstüne gelir)
- Asma tavan üretimi (Faz 1D)
- AutoCAD'de çizim
- Rhino'dan Revit'e aktarma
- Metraj
- Render
- Bağlantı programlarının kuruluma eklenmesi
