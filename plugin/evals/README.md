# Ön kapı eval seti

Bu klasör, `istek-karsilama` ön kapısının sentetik isteklerle sınandığı eval vakalarını içerir.
Kullanıcının kendi Claude hesabıyla yerelde çalışır; CI'da çalışmaz. Bakımcı ve şampiyonlar içindir.

## Kapı komutu (repo kökünden)

```
claude plugin eval plugin --trust-plugin --allow-tools Write Edit --ablation none --threshold 0.8 --no-publish --max-cost-usd 10 --json plugin/evals/results/son.json
```

Uzun sürer (10 vaka x 3 koşu, 10 dakikadan fazla); arka planda çalıştırın. Sonuçlar `plugin/evals/results/` altına
gider ve git'e girmez. Hata ayıklarken `--case <ad> --runs 1` kullanın.

Bütçe: komuttaki `--max-cost-usd 10`, planın bu set için koyduğu üst sınırdır (tavan), harcama değildir. Aşağıdaki
kayıtlı koşu daha sıkı bir sınırla, `--max-cost-usd 4` ile yapıldı (o gün 9 vaka vardı, tahmini 3,7 USD tuttu).
10 vakalık set biraz daha pahalıdır ve 4 sınırı yetmeyebilir; bu yüzden komutta tavan yazılıdır.

## Neden `--allow-tools Write Edit` şart

`Write` ve `Edit` salt okunur araç sayılmaz. Bu bayrak olmadan koşuda bu araçlar hiç verilmez, yani ajan yazamaz ve
`yazma-yok-*` (`max: 0`) ölçütleri boşuna geçer. Bayrakla ajan yazabilir; ölçüt "onaydan önce yazmadı" demek olur.

## `--ablation with-without` ne ekler

Her vakayı bir de eklentisiz koşturur ve fark (Δ) hesaplar. Maliyeti yaklaşık iki katıdır (tam set için yaklaşık 7,5 USD).
Bu modda `tool_used: Skill` ölçütleri skordan çıkar, yalnızca "eklenti devreye girdi mi" göstergesi olur.
Varsayılan olarak bu mod açıktır; kapı komutunda bütçe için `--ablation none` kullanılır.

## Sabit bağlantı (hard link) sorunu

Eval aracı, eklenti içinde birden çok adı olan dosyayı reddeder. `plugin/.venv` uv'nin sabit bağlantılarıyla
kurulursa tüm vakalar "hard link" hatasıyla 0 alır. Çözüm:

```
rm -rf plugin/.venv
UV_LINK_MODE=copy uv sync --project plugin
```

## Güvenilirlik

Yargıç (`davranis.md`) oldukça değişkendir: aynı yanıtı bir koşuda geçirip ötekinde kaldırabilir. 0,83 ortalamalı
vakalar kırılgandır. Gerçek kapı, pilotta toplanan gerçek başarısız istekler setidir (dev'den main'e geçiş ölçütü);
bu sentetik set yalnızca erken uyarıdır.

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

Genel 0,92; 9/9 vaka >= 0,8. Bu sonuç `davranis` yargıcına ön bilgi cümlesi eklenmeden önceki sürümle alındı.

## Yeni, henüz koşulmamış

- `ofis-disi`: olumsuz vaka ("merhaba, nasılsın?"); ön kapı devreye GİRMEMELİ (`tool_used Skill`, `max: 0`).
- Her `davranis.md` başına ön bilgi cümlesi eklendi; `belirsiz` ve `metraj-liste` için program-bağlı maddesi koşullu yazıldı.
- Her `davranis.md`'deki FAIL cümlesinin program maddesi çift olumsuzluk olmadan yeniden yazıldı; anlamı aynı.
