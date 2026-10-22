# Ön Kapı Eval Seti

Bu klasör, istek karşılama katmanının (ön kapı, `istek-karsilama` skill'i) sentetik isteklerle sınandığı eval
vakalarını içerir. Eval, çalıştıran kişinin Claude hesabıyla yerel olarak çalışır; CI'da çalıştırılmaz. Bakımcılar ve
pilot kullanıcılar için hazırlanmıştır.

## Kapı komutu (repo kök dizininden)

```
claude plugin eval plugin --trust-plugin --allow-tools Write Edit --ablation none --threshold 0.8 --no-publish --max-cost-usd 10 --json plugin/evals/results/son.json
```

Koşu uzun sürer (10 vaka x 3 koşu, 10 dakikadan fazla); arka planda çalıştırılması önerilir. Sonuçlar
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
