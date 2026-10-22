# Başlayın

Bu eklenti, Revit, AutoCAD ve Rhino işlerinde size yardım eder. İsteğinizi anlar, önce plan gösterir, siz onaylayınca uygular. Her şeyi bilmez. Bazen yanlış anlar. Bu yüzden her adımda sizden onay ister.

Önce [neler yapabildiğine](NELER-YAPABILIR.md) bakın. Takıldığınızda [sorun giderme](SORUN-GIDERME.md) sayfası var. Bilmediğiniz bir kelime çıkarsa [sözlüğe](SOZLUK.md) bakın.

Hangi programı kullanıyorsanız onun yolunu izleyin.

## Terminal kullanıyorsanız

Claude Code'u terminalde kullanıyorsanız kurulum tek satırdır.

1. Başlat menüsüne `cmd` yazıp komut penceresini açın.
2. Şu satırı yapıştırıp Enter'a basın:

```
powershell -ExecutionPolicy Bypass -c "iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
```

Pilot süresince bu satır henüz çalışmaz; onun yerine aşağıdaki [Kanallar](#kanallar) bölümündeki `dev` satırını kullanın.

Satır yapıştırmak istemezseniz, repo klasörünün tamamını indirdiyseniz `kur.cmd` dosyasına çift tıklayın. Aynı işi yapar. (`kur.cmd` yanında `kur.ps1` dosyası olmadan çalışmaz.)

`kur.ps1` sırayla şunları yapar:

- Gerekli küçük programları kurar ([uv](SOZLUK.md) ve Python 3.12).
- Claude Code bilgisayarda kuruluysa eklentiyi ([plugin](SOZLUK.md)) ekler, kurar ve otomatik güncellemeyi açar. Eski ayarlarınızın yedeğini `settings.json.aec-yedek` adıyla saklar.
- Revit tarafında bir şey kurmaz. Yalnızca neyin eksik olduğunu yazar.

Bittiğinde Claude Code'u kapatıp yeniden açın.

Claude Code'u her zaman projenin klasöründe başlatın. Komut penceresinde önce proje klasörüne geçin, sonra `claude` yazın:

```
cd /d "D:\Projeler\Örnek Konut"
claude
```

`/aec:proje-baslat` proje bilgilerini bu klasöre yazar. Claude'u kendi kullanıcı klasörünüzde açarsanız bu komut hiçbir şey yazmaz ve sizi uyarır.

## Cowork kullanıyorsanız

Claude masaüstü uygulamasındaki Cowork'ü kullanıyorsanız iki adım vardır.

**1. Önce yukarıdaki tek satırı çalıştırın** ("Terminal kullanıyorsanız" bölümündeki satırın aynısı; pilot süresince [Kanallar](#kanallar) bölümündeki `dev` satırı). Cowork bilgisayarında Claude Code komutu yoksa satır yalnızca uv ve Python 3.12'yi kurar, eklenti adımını atlar ve size Cowork yolunu hatırlatır. Terminali de kullanan bilgisayarlarda eklentiyi ekler ve otomatik güncellemeyi açar; ayar dosyasının yedeğini alır. Bunu yalnızca bir kez yaparsınız. Repo klasörünün tamamını indirdiyseniz `kur.cmd` de aynı işi yapar.

**2. Eklentiyi ekleyin.**

1. Claude uygulamasında **Customize** bölümünü açın.
2. **Plugins** sekmesine girin.
3. **Add marketplace** (mağaza ekle) düğmesine basın.
4. Şunu yazın: `modularbelen-del/aec-harness`
5. **Sync automatically** (otomatik eşitle) seçeneğini açın. Böylece yeni sürümler kendiliğinden gelir.
6. Listeden `aec` eklentisini açın.

**Uyarı:** Revit gibi bilgisayarınızdaki programlara bağlanmak için oturumun "bilgisayarınızda" çalışması gerekir. Oturumu başlatırken bu seçeneği seçin. Bulutta çalışan oturum Revit'i göremez.

Cowork'te karşılama kartı bazen gelmeyebilir. Bu normaldir. İsteğinizi yazın; çoğu zaman eklenti yine çalışır. Çalışmazsa `/aec:kontrol-et` yazın.

## İlk 3 deneme

Kurulumdan sonra sırayla şunları deneyin. Üçü de zararsızdır. Yalnızca `/aec:proje-baslat` dosya yazar: projenin klasörüne `.aec/proje.md` dosyasını ekler ve `CLAUDE.md` dosyasına kısa bir bölüm ekler; sizin yazdıklarınıza dokunmaz. Öbür ikisi yalnızca okur.

1. **`/aec:kontrol-et`** yazın. Kurulumun sağlam olup olmadığını ve Revit bağlantısını söyler. Eksik varsa ne yapacağınızı yazar.
2. **`/aec:proje-baslat`** yazın. Birkaç soru sorar (proje adı, birim, kat adları gibi). Önce hangi klasöre yazacağını söyler; klasör yanlışsa söyleyin. Cevaplarınızı o klasördeki bir dosyaya yazar. Sonra aynı şeyleri tekrar sormaz.
3. **`/aec:yardim`** yazın. Bugün neler yapabildiğini gösterir; Revit gerekmez. Revit bağlantınız kuruluysa bir iş de deneyebilirsiniz; nasıl yazacağınızı [örnek isteklerden](ORNEK-ISTEKLER.md) görün. Revit bağlantısı yoksa o iş için yalnızca plan çıkar.

Kendi dosyanızla çalışmadan önce [güvenlik kurallarına](GUVENLIK.md) bir göz atın. Beş dakikanızı alır.

## Kanallar

Çoğu kişi için `main` kanalı doğrudur. Bu kanal denenmiş, kararlı sürümdür. Denemeleri ilk görmek isteyen şampiyonlar `dev` kanalını kurar. Bu satırı Win+R penceresine ya da `cmd` penceresine yazın:

```
powershell -ExecutionPolicy Bypass -c "$env:AEC_KANAL='dev'; iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/dev/kur.ps1).TrimStart([char]0xFEFF))"
```

Pilot süresince yalnızca bu `dev` satırı çalışır. Yukarıdaki `main` satırı, değişiklikler pilottan sonra `main` kanalına geçince çalışacak.

İki kanalı aynı anda kuramazsınız. Biri ötekinin yerine geçer.
