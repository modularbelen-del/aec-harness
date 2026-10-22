# Sorun giderme

Bir şey beklediğiniz gibi çalışmadıysa sebep çoğu zaman küçük bir bağlantı eksiğidir. Önce `/aec:kontrol-et` yazın. Ne eksikse söyler.

## "Revit bağlı değil"

Revit bağlantısı yalnızca ofisin kurduğu bilgisayarlarda çalışır. Şunlara bakın:

1. Revit açık mı ve bir proje açık mı?
2. Cowork kullanıyorsanız oturum "bilgisayarınızda" mı çalışıyor? ([Başlayın](BASLA.md))
3. Hâlâ olmuyorsa `/aec:kontrol-et` çıktısını ofisteki sorumluya gösterin.

AutoCAD ve Rhino bağlantıları yakında. Onlar için bu mesaj beklenen bir durumdur. ([Neler yapabilir](NELER-YAPABILIR.md))

## "hook error"

Açılışta ya da isteğinizden sonra "hook error" yazısı görürseniz ([hook nedir?](SOZLUK.md)) sebep çoğu zaman şunlardan biridir:

- İlk açılışta yardımcı program gereken dosyaları indirirken süre dolmuştur. İkinci açılışta genelde düzelir.
- Cowork ortamı yardımcı programı çalıştıramamıştır.

(`uv` eksikse bu yazı çıkmaz; o durumda karşılama kartı sessizce gelmez. Bunun için aşağıdaki "uv bulunamadı" kısmına bakın.)

Ne yapmalı:

1. Oturumu kapatıp yeniden açın.
2. Olmazsa [Başlayın](BASLA.md) sayfasındaki tek satırlık kurulumu yeniden çalıştırın.
3. Yine olmazsa ofisteki sorumluya (şampiyona) haber verin.

Bu sırada iş çoğu zaman yine çalışır, yalnızca karşılama kartı gelmez; çalışmazsa `/aec:kontrol-et` yazın.

## "uv bulunamadı"

[uv](SOZLUK.md), eklentinin küçük yardımcı programlarını çalıştıran bir programdır. Kurmak için:

- Terminal kullanıyorsanız [Başlayın](BASLA.md) sayfasındaki satırı yeniden çalıştırın.
- Cowork kullanıyorsanız aynı tek satırı çalıştırın. Repo klasörünün tamamını indirdiyseniz `kur.cmd` dosyasına çift tıklamak da olur.

Sonra Claude'u kapatıp yeniden açın.

## Kart gelmiyor (Cowork)

Cowork'te karşılama kartı bazen görünmeyebilir. Bu bir hata değildir. İsteğinizi yazın; çoğu zaman eklenti yine çalışır. Çalışmazsa `/aec:kontrol-et` yazın.

Eklenti hiç yanıt vermiyorsa:

1. Customize > Plugins bölümünde `aec` açık mı?
2. Marketplace için "Sync automatically" açık mı?
3. Yeni bir oturum başlatın.

## Otomatik güncelleme kapalı görünüyor

`/plugin` yazın, sırayla Marketplaces > aec-office > Enable auto-update yolunu izleyin.

## Hâlâ olmuyor

Ekranda ne yazdığını kopyalayın. Hangi isteği yazdığınızı ekleyin. Müşteri bilgisi varsa silin. Ofisteki sorumluya gönderin.
