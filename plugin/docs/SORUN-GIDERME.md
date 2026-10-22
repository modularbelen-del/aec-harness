# Sorun giderme

Bir şey çalışmadıysa yapay zekâ bozuk demek değildir. Çoğu zaman küçük bir bağlantı eksiğidir. Önce `/aec:kontrol-et` yazın. Ne eksikse söyler.

## "Revit bağlı değil"

Revit bağlantısı yalnızca ofisin kurduğu bilgisayarlarda çalışır. Şunlara bakın:

1. Revit açık mı ve bir proje açık mı?
2. Cowork kullanıyorsanız oturum "bilgisayarınızda" mı çalışıyor? ([Başlayın](BASLA.md))
3. Hâlâ olmuyorsa `/aec:kontrol-et` çıktısını ofisteki sorumluya gösterin.

AutoCAD ve Rhino bağlantıları henüz deneme aşamasındadır. Onlar için bu mesaj beklenen bir durumdur. ([Neler yapabilir](NELER-YAPABILIR.md))

## "hook error"

Açılışta ya da isteğinizden sonra "hook error" yazısı görürseniz çoğu zaman bilgisayarda `uv` yoktur. Aşağıdaki "uv bulunamadı" kısmına bakın. İş yine de çalışır; yalnızca karşılama kartı gelmez. ([hook nedir?](SOZLUK.md))

## "uv bulunamadı"

`uv`, eklentinin küçük yardımcı programlarını çalıştıran bir programdır. Kurmak için:

- Terminal kullanıyorsanız [Başlayın](BASLA.md) sayfasındaki satırı yeniden çalıştırın.
- Cowork kullanıyorsanız `kur.cmd` dosyasına çift tıklayın.

Sonra Claude'u kapatıp yeniden açın.

## Kart gelmiyor (Cowork)

Cowork'te karşılama kartı bazen görünmeyebilir. Bu bir hata değildir; eklenti yine çalışır. İsteğinizi yazın, plan gelecektir.

Eklenti hiç yanıt vermiyorsa:

1. Customize > Plugins bölümünde `aec` açık mı?
2. Marketplace için "Sync automatically" açık mı?
3. Yeni bir oturum başlatın.

## Hâlâ olmuyor

Ekranda ne yazdığını kopyalayın. Hangi isteği yazdığınızı ekleyin. Müşteri bilgisi varsa silin. Ofisteki sorumluya gönderin.
