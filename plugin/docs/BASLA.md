# Kurulum ve İlk Kullanım

Bu eklenti, Revit, AutoCAD ve Rhino ile yürütülen işlerde destek sağlar. İsteği yorumlar, önce bir plan sunar ve onay alındıktan sonra uygular. Eklentinin bilgisi sınırlıdır ve istekleri zaman zaman yanlış yorumlayabilir; bu nedenle her adımda onay istenir.

Eklentinin kapsamı [Mevcut Kapsam](NELER-YAPABILIR.md) sayfasında açıklanmıştır. Karşılaşılan sorunlar için [Sorun Giderme](SORUN-GIDERME.md), terimler için [Sözlük](SOZLUK.md) sayfasına başvurulabilir.

Kurulum, kullanılan uygulamaya göre aşağıdaki iki yoldan biriyle yapılır.

## Terminal ile kurulum

Claude Code terminalde kullanılıyorsa kurulum tek satırlık bir komutla yapılır.

1. Başlat menüsüne `cmd` yazılarak komut penceresi açılır.
2. Aşağıdaki satır yapıştırılır ve Enter tuşuna basılır:

```
powershell -ExecutionPolicy Bypass -c "iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
```

Pilot dönemi boyunca bu satır çalışmaz; bunun yerine [Kanallar](#kanallar) bölümündeki `dev` satırı kullanılmalıdır.

Repo klasörünün tamamı indirilmişse, satır yapıştırmak yerine `kur.cmd` dosyasına çift tıklanabilir; dosya aynı işlemi yapar. (`kur.cmd`, aynı klasörde `kur.ps1` dosyası bulunmadan çalışmaz.)

`kur.ps1` sırasıyla şu işlemleri yapar:

- Gerekli yardımcı programları kurar ([uv](SOZLUK.md) ve Python 3.12).
- Claude Code bilgisayarda kuruluysa eklentiyi ([plugin](SOZLUK.md)) ekler, kurar ve otomatik güncellemeyi açar. Mevcut ayarların yedeğini `settings.json.aec-yedek` adıyla saklar.
- Revit tarafında kurulum yapmaz; yalnızca eksik bileşenleri raporlar.

Kurulum tamamlandığında Claude Code kapatılıp yeniden açılmalıdır.

Claude Code'u her zaman projenin klasöründe başlatınız. Bunun için komut penceresinde önce proje klasörüne geçilir, ardından `claude` yazılır:

```
cd /d "D:\Projeler\Örnek Konut"
claude
```

`/aec:proje-baslat` proje bilgilerini bu klasöre yazar. Claude kullanıcı klasöründe açılmışsa komut hiçbir dosya yazmaz ve uyarı verir.

## Cowork ile kurulum

Claude masaüstü uygulamasındaki Cowork kullanılıyorsa kurulum iki adımdan oluşur.

**1. Kurulum satırının çalıştırılması.** "Terminal ile kurulum" bölümündeki satır çalıştırılır (pilot dönemi boyunca [Kanallar](#kanallar) bölümündeki `dev` satırı). Bilgisayarda Claude Code komutu bulunmuyorsa betik yalnızca uv ve Python 3.12'yi kurar, eklenti adımını atlar ve Cowork kurulum adımlarına yönlendirir. Claude Code'un da kurulu olduğu bilgisayarlarda eklentiyi ekler, otomatik güncellemeyi açar ve ayar dosyasını yedekler. Bu adım yalnızca bir kez uygulanır. Repo klasörünün tamamı indirilmişse `kur.cmd` dosyası da aynı işlemi yapar.

**2. Eklentinin eklenmesi.**

1. Claude uygulamasında **Customize** bölümü açılır.
2. **Plugins** sekmesine geçilir.
3. **Add marketplace** (mağaza ekle) düğmesine tıklanır.
4. Adres alanına `modularbelen-del/aec-harness` yazılır.
5. **Sync automatically** (otomatik eşitle) seçeneği açılır. Bu seçenekle yeni sürümler otomatik olarak yüklenir.
6. Listeden `aec` eklentisi etkinleştirilir.

**Uyarı:** Revit gibi yerel programlara bağlanabilmek için oturumun "bilgisayarınızda" seçeneğiyle başlatılması gerekir. Bulutta çalışan oturum yerel programlara erişemez.

Cowork'te istek karşılama katmanının (ön kapı) kartı her istekte görüntülenmeyebilir; bu beklenen bir durumdur. Bu durumda istek normal biçimde yazılır; eklenti çoğu durumda yine devreye girer. Devreye girmezse `/aec:kontrol-et` komutu çalıştırılmalıdır.

## İlk kullanım

Kurulumun ardından aşağıdaki üç komutun sırasıyla çalıştırılması önerilir. Bu komutlar modellerde ve çizimlerde değişiklik yapmaz. Yalnızca `/aec:proje-baslat` dosya yazar: proje klasörüne `.aec/proje.md` dosyasını ekler ve `CLAUDE.md` dosyasına kısa bir bölüm ekler; dosyadaki mevcut metne dokunmaz. Diğer iki komut yalnızca okuma yapar.

1. **`/aec:kontrol-et`**: Kurulumun ve Revit bağlantısının durumunu raporlar. Eksik bir bileşen varsa yapılması gerekeni belirtir.
2. **`/aec:proje-baslat`**: Proje adı, birim ve kat adları gibi birkaç soru sorar. Önce hangi klasöre yazılacağını bildirir; klasör hatalıysa bu aşamada belirtilmelidir. Yanıtlar o klasördeki bir dosyaya kaydedilir ve sonraki isteklerde yeniden sorulmaz.
3. **`/aec:yardim`**: Kullanımdaki özellikleri gösterir; Revit gerektirmez. Revit bağlantısı kuruluysa örnek bir iş de denenebilir; istek yazımı için [Örnek İstekler](ORNEK-ISTEKLER.md) sayfasına başvurulabilir. Revit bağlantısı yoksa bu iş için yalnızca plan hazırlanır.

Proje dosyalarıyla çalışmaya başlamadan önce [Güvenlik İlkeleri](GUVENLIK.md) sayfasının okunması gerekir.

## Kanallar

Kullanıcıların büyük çoğunluğu için doğru kanal `main` kanalıdır; bu kanal sınanmış, kararlı sürümü içerir. Yeni özellikleri önceden deneyen pilot kullanıcılar `dev` kanalını kurar. Aşağıdaki satır Win+R ya da `cmd` penceresine yazılır:

```
powershell -ExecutionPolicy Bypass -c "$env:AEC_KANAL='dev'; iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/dev/kur.ps1).TrimStart([char]0xFEFF))"
```

Pilot dönemi boyunca yalnızca bu `dev` satırı çalışır. Yukarıdaki `main` satırı, değişiklikler pilot dönemin ardından `main` kanalına aktarıldığında çalışacaktır.

İki kanal aynı bilgisayarda birlikte kurulamaz; sonradan kurulan kanal öncekinin yerini alır.
