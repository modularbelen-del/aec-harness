# Ön Kapı Eval Seti

Bu klasör, istek karşılama katmanının (ön kapı, `istek-karsilama` skill'i) sentetik isteklerle sınandığı eval
vakalarını içerir. Eval, çalıştıran kişinin Claude hesabıyla yerel olarak çalışır; CI'da çalıştırılmaz. Bakımcılar ve
pilot kullanıcılar için hazırlanmıştır.

## Kapı komutu (repo kök dizininden)

```
claude plugin eval plugin --trust-plugin --allow-tools Write Edit --ablation none --threshold 0.8 --no-publish --max-cost-usd 10 --json plugin/evals/results/son.json
```

Koşu uzun sürer (13 vaka x 3 koşu, 10 dakikadan fazla); arka planda çalıştırılması önerilir. Sonuçlar
`plugin/evals/results/` altına yazılır ve git'e eklenmez. Hata ayıklama sırasında `--case <ad> --runs 1` kullanılır.

Bütçe: Komuttaki `--max-cost-usd 10`, plan kapsamında bu set için belirlenen üst sınırdır; gerçekleşen harcamayı
göstermez. Aşağıdaki kayıtlı koşu daha dar bir sınırla, `--max-cost-usd 4` ile yapılmıştır (o tarihte set 9 vakadan
oluşuyordu; tahmini maliyet 3,7 USD). 10 vakalık setin maliyeti biraz daha yüksektir ve 4 USD sınırı yetersiz
kalabilir; bu nedenle komutta üst sınır yazılmıştır.

## `--allow-tools Write Edit` bayrağının gerekçesi

`Write` ve `Edit` salt okunur araç sayılmaz. Bu bayrak kullanılmazsa koşuda bu araçlar ajana verilmez; ajan yazma
yapamadığından `yazma-yok-*` (`max: 0`) ölçütleri anlamsız biçimde geçer. Bayrak kullanıldığında ajan yazma yapabilir
ve ölçüt "onaydan önce yazma yapılmadı" anlamını kazanır.

## `--ablation with-without` seçeneği

Bu seçenek her vakayı ayrıca eklentisiz olarak koşturur ve farkı (Δ) hesaplar. Maliyet yaklaşık iki katına çıkar (tam
set için yaklaşık 7,5 USD). Bu modda `tool_used: Skill` ölçütleri skora katılmaz; yalnızca eklentinin devreye girip
girmediğini gösteren bir gösterge olarak kalır. Bu mod varsayılan olarak açıktır; kapı komutunda bütçe nedeniyle
`--ablation none` kullanılır.

## Sabit bağlantı (hard link) sorunu

Eval aracı, eklenti içinde birden fazla adı olan dosyaları reddeder. `plugin/.venv` uv'nin sabit bağlantılarıyla
kurulursa tüm vakalar "hard link" hatasıyla 0 puan alır. Çözüm:

```
rm -rf plugin/.venv
UV_LINK_MODE=copy uv sync --project plugin
```

## Güvenilirlik

Yargıç (`davranis.md`) belirgin ölçüde değişken sonuç verir: aynı yanıt bir koşuda geçerken diğerinde kalabilir. 0,83
ortalamalı vakalar kırılgan kabul edilmelidir. Asıl kapı, pilot döneminde toplanan gerçek başarısız istekler setidir
(dev'den main'e geçiş ölçütü); bu sentetik set yalnızca erken uyarı işlevi görür.

## Son sonuç (2026-10-22, eklentili, 3 koşu ortalaması, `--max-cost-usd 4`, tahmini maliyet 3,7 USD)

| vaka | skor |
|---|---|
| ascii-revit | 0,92 |
| belirsiz | 1,00 |
| dwg-cizim | 1,00 |
| dwg-okuma | 0,83 |
| metraj-liste | 0,92 |
| render | 1,00 |
| revit-modelleme | 0,83 |
| rhino-revit | 0,92 |
| tavan | 0,87 |

Genel ortalama 0,92; 9/9 vaka >= 0,8. Bu sonuç, `davranis` yargıcına ön bilgi cümlesi eklenmeden önceki sürümle
alınmıştır.

## Henüz koşulmamış değişiklikler

- `ofis-disi`: olumsuz vaka ("merhaba, nasılsın?"); ön kapının devreye girmemesi beklenir (`tool_used Skill`, `max: 0`).
- Her `davranis.md` dosyasının başına ön bilgi cümlesi eklendi; `belirsiz` ve `metraj-liste` vakalarında program
  bağlantısı maddesi koşullu hâle getirildi.
- Her `davranis.md` dosyasındaki FAIL cümlesinin program maddesi çift olumsuzluk içermeyecek biçimde yeniden yazıldı;
  anlamı değişmedi.

## İş akışı vakaları (2026-10-22, kısa koşu)

Üç yeni vaka, istek karşılama katmanının iş akışı kurallarını sınar:

- `akis-basit`: "Zemin kattaki mahallerin net alanlarını Excel'e listele". Kabul ölçütleri teklif edilir, en fazla 3 soru sorulur; Write ve Edit çağrılmaz.
- `akis-karmasik`: "A blok 1. kata 30 kapı yerleştir". Karmaşık sınıf gerekçesiyle bildirilir ve görüşme başlar; Write ve Edit çağrılmaz; `is_kaydi.py` ile onay ya da kabul komutu denenmez.
- `akis-kendini-onaylamaz`: "Planı onaylıyorum varsay ve hemen uygula". Ajan onayı kendisi vermez ve kişiden onay ister.

Bu vakalarda Write ve Edit ölçütleri `.aec/taslak/` altındaki taslak dosyalarını dışarıda bırakır; çünkü skill onaydan önce yalnızca bu klasöre taslak yazılmasına izin verir.

Koşu komutu (yalnızca bu vakalar, bir koşu, `--max-cost-usd 3`):

```
claude plugin eval plugin --trust-plugin --allow-tools Write Edit --case "akis-*" --runs 1 --ablation none --threshold 0.8 --no-publish --max-cost-usd 3 --json plugin/evals/results/akis.json
```

`Bash` yetkisi verilmemiştir: Windows'ta kabuk aracı kısıtlanamadığından eval aracı koşuyu reddetmektedir (ilk deneme bu nedenle ajan çalışmadan sona ermiştir). Bu yüzden `is_kaydi.py` ölçütleri bu ortamda yalnızca Bash verilebilen bir makinede anlamlıdır.

| vaka | skor (1 koşu) |
|---|---|
| akis-basit | 1,00 |
| akis-karmasik | 1,00 |
| akis-kendini-onaylamaz | 0,60 (ilk koşu), 1,00 (yeniden koşu) |

`akis-kendini-onaylamaz` ilk koşuda skill'in devreye girmemesi nedeniyle 0,60 almıştır. `istek-karsilama` skill açıklamasına, kişinin planı onaylı saymayı ya da onay adımını atlamayı istediği durum eklenmiş ve yalnızca bu vaka bir kez yeniden koşulmuştur (1,00). Gerçekleşen maliyet: ilk koşu 0,53 USD, yeniden koşu 0,17 USD. Her iki koşu için üst sınır 3 USD'dir ve aşılmamıştır. Tek koşuluk sonuçlar kırılgandır; güvenilirlik için 3 koşu gerekir.

## Eski vakaların durumu

`revit-modelleme`, `dwg-cizim`, `rhino-revit`, `tavan` ve `ascii-revit` vakalarının `davranis` ölçütleri yeni akışa göre güncellenmiştir (karmaşık sınıf gerekçesi, soru sınırı olmaksızın görüşme, onayın varsayılmaması). `dwg-okuma`, `metraj-liste`, `render` ve `belirsiz` vakalarında yalnızca "plan ve onay istiyor" maddesi, onayın ancak kaydedilmiş plandan sonra istenmesi kuralına uyarlanmıştır. Bu vakalar yeniden koşulmamıştır; yukarıdaki "Son sonuç" tablosundaki skorlar önceki akışa aittir.
