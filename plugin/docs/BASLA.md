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

Satır yapıştırmak istemezseniz `kur.cmd` dosyasına çift tıklayın. Aynı işi yapar.

`kur.ps1` sırayla şunları yapar:

- Gerekli küçük programları kurar (uv ve Python 3.12).
- Eklentiyi ekler ve kurar.
- Otomatik güncellemeyi açar. Eski ayarlarınızın yedeğini `settings.json.aec-yedek` adıyla saklar.
- Revit tarafında bir şey kurmaz. Yalnızca neyin eksik olduğunu yazar.

Bittiğinde Claude Code'u kapatıp yeniden açın.

## Cowork kullanıyorsanız

Claude masaüstü uygulamasındaki Cowork'ü kullanıyorsanız iki adım vardır.

**1. Önce `kur.cmd`.** Ofisten aldığınız ya da GitHub sayfasından indirdiğiniz `kur.cmd` dosyasına çift tıklayın. Eklentinin ihtiyaç duyduğu küçük programı (uv) kurar. Bunu yalnızca bir kez yaparsınız.

**2. Eklentiyi ekleyin.**

1. Claude uygulamasında **Customize** bölümünü açın.
2. **Plugins** sekmesine girin.
3. **Add marketplace** düğmesine basın.
4. Şunu yazın: `modularbelen-del/aec-harness`
5. **Sync automatically** (otomatik eşitle) seçeneğini açın. Böylece yeni sürümler kendiliğinden gelir.
6. Listeden `aec` eklentisini açın.

**Uyarı:** Revit gibi bilgisayarınızdaki programlara bağlanmak için oturumun "bilgisayarınızda" çalışması gerekir. Oturumu başlatırken bu seçeneği seçin. Bulutta çalışan oturum Revit'i göremez.

Cowork'te karşılama kartı bazen gelmeyebilir. Bu normaldir. Eklenti yine de çalışır; isteğinizi yazın, plan gelir.

## İlk 3 deneme

Kurulumdan sonra sırayla şunları deneyin. Üçü de zararsızdır, hiçbir dosyayı değiştirmez.

1. **`/aec:kontrol-et`** yazın. Kurulumun sağlam olup olmadığını ve Revit bağlantısını söyler. Eksik varsa ne yapacağınızı yazar.
2. **`/aec:proje-baslat`** yazın. Birkaç soru sorar (proje adı, birim, kat adları gibi). Cevaplarınızı projenin klasöründeki bir dosyaya yazar. Sonra aynı şeyleri tekrar sormaz.
3. **Bir örnek istek yazın.** Mesela: `Zemin kat planındaki duvarları listele.` Nasıl yazacağınızı [örnek isteklerden](ORNEK-ISTEKLER.md) görebilirsiniz.

Kendi dosyanızla çalışmadan önce [güvenlik kurallarına](GUVENLIK.md) bir göz atın. Beş dakikanızı alır.

## Kanallar

Çoğu kişi için `main` kanalı doğrudur. Bu kanal denenmiş, kararlı sürümdür. Denemeleri ilk görmek isteyen şampiyonlar `dev` kanalını kurar. Bu satırı Win+R penceresine ya da `cmd` penceresine yazın:

```
powershell -ExecutionPolicy Bypass -c "$env:AEC_KANAL='dev'; iex ((irm https://raw.githubusercontent.com/modularbelen-del/aec-harness/main/kur.ps1).TrimStart([char]0xFEFF))"
```

İki kanalı aynı anda kuramazsınız. Biri ötekinin yerine geçer.
