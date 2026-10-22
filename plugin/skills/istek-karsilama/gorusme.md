# Görüşme rehberi (karmaşık iş)

Bu rehber karmaşık işte izlenir: Revit, Rhino ya da AutoCAD'de çizim veya model oluşturan ya da değiştiren her iş.
Amaç, uygulamaya geçmeden önce kişinin ne istediğini ve neden istediğini anlamak ve işin nasıl kabul edileceğini
baştan belirlemektir. Neden'i anlayan ajan, kişinin hiç söylemediği küçük kararları da onun vereceği gibi verir;
tahminle yapılan iş ise bu kararları yanlış verir.

## İlk mesaj
- İşin karmaşık iş olarak yürütüleceğini ve gerekçesini bir cümleyle söyle: "Bu iş Revit modelini değiştirdiği için
  karmaşık iş olarak yürütülecektir; önce kısa bir görüşme yapılacak, ardından tarif, plan ve görevler ayrı ayrı
  onayınıza sunulacaktır."
- Gereken araç bu oturumda yoksa kartın "Yapamıyorsam" metnini bu mesajda söyle.
- Proje MD'sinden ve açık model ya da çizimden okuduklarını kısaca yaz; bilinen bir şeyi yeniden sorma.
- Ardından ilk konunun (amaç) sorularıyla başla.

## Konular
Görüşme aşağıdaki konularda sırayla ilerler. Bunlar okunacak bir soru listesi değildir; kapsanacak alanlardır.
Kişinin isteği bir konuyu zaten açıklıyorsa o konuyu özetle geç.

1. **Amaç:** iş ne için yapılıyor; sonuç nerede kullanılacak (pafta, sunum, metraj, koordinasyon); iş ne zaman
   tamamlanmış sayılacak.
2. **Kapsam:** hangi dosya (kopya model ya da çizim); hangi kat, bölge ve öğeler; adetler; ölçülerin kaynağı.
3. **Kapsam dışı:** bu işte yapılmayacak olanlar; dokunulmayacak dosya, kat ve öğeler.
4. **Mevcut durum:** model ya da çizimde şu an ne var; daha önce ne denendi; yüklü aileler ve tipler, katman düzeni.
5. **Kabul ölçütleri:** iş bittiğinde neyin, hangi yöntemle kontrol edileceği. Kartın "Kabul ölçütleri"
   bölümündeki varsayılanlardan başla ve işe göre kesinleştir. Her ölçüt ölçülebilir olsun; varsa beklenen değeri ve
   toleransı yaz. Yöntemler: `revit-okuma`, `dosya`, `olcu` (Faz 1C öncesinde DOĞRULANAMADI olabilir), `kisi-gorsel`.

## Soru sorma
- Birbirinden bağımsız soruları tek mesajda numaralı liste hâlinde sor; birbirine bağlı soruları (bir yanıtın
  ötekini değiştirdiği soruları) tek tek sor. Bu, ofisin kuralıdır.
- Somut sor: "Kapılar hangi aks aralığına yerleştirilecek?" gibi. Önce kişinin kendi sözleriyle anlatmasını iste;
  seçenek yalnızca kişi kararsız kaldığında sun. Kişi "siz önerin" derse somut bir öneri yap ve VARSAYIM diye işaretle.
- Seçenekli sorularda `AskUserQuestion` kullanılabilir; onay ve kabul sorularında kullanılmaz.
- Araçla okunabilen bir şeyi sorma, oku: seviyeler, aileler, tipler, katmanlar. Ölçü görselden alınmaz.
- Görüşmede yalnızca okuma araçları kullanılır; hiçbir yazma aracı çağrılmaz (tek istisna: aşağıdaki kesin kuraldaki
  `.aec/taslak/` taslağı).

## Bölüm özeti ve teyit
- Bir konuyu anlatabilecek kadar anladığında o konuyu 150–250 kelimelik bir özetle kişiye geri anlat, sonra sıradaki
  konunun sorularına geç. Özet ve sorular dönüşümlü ilerler; son özet kalan konuları kapsar.
- Kişinin söylediğini kişinin sözü olarak yaz. Kendi tahminini VARSAYIM etiketiyle yaz: "VARSAYIM: kapılar duvar
  ortasına yerleştirilecektir."
- Her özeti teyit isteyen bir cümleyle bitir: "Eksik ya da hatalı bir nokta varsa belirtiniz."
- Kişinin düzelttiği noktayı bir sonraki özette düzeltilmiş hâliyle yaz.

## İşi boyutlandırma
Konular netleştiğinde işin büyüklüğünü bir cümleyle söyle. Boyut yalnızca belgelerin uzunluğunu belirler; işin
sınıfı (karmaşık) değişmez.

| Boyut | Belgeler | Uygulama |
|---|---|---|
| Tek adımlı küçük değişiklik (ör. bir kapının tipini değiştirme) | Kısa tarif, tek görevli plan | Tek görev |
| Birkaç adımlı iş | Tarif, plan ve görevler | Görev görev |
| Birbirinden bağımsız birkaç iş | Her iş için ayrı iş kaydı | Sırası kişiyle belirlenir, işler tek tek yürütülür |

Uygulama sırasında iş büyürse dur ve durumu kişiye söyle. Henüz hiçbir şey yazılmadıysa planı yeniden onaya sun. Bir
şey yazıldıktan sonra plan yeniden kaydedilemez: kontrol yapılır, kişi kabulde reddederse yeni plan `reddedildi`
durumundan kaydedilir ya da iş kişiye bildirilerek iptal edilir (SKILL.md, 8. adım).

## Görüşmenin sonu
- Kabul ölçütleri kesinleşince iş kaydını aç ve ölçütleri kaydet (SKILL.md, 4. adım).
- Tarifi `sablonlar/tarif.md` şablonuyla yaz. Kişinin henüz karar vermediği en fazla 3 nokta tarifte işaretlenir;
  bu noktaları onay mesajında açık uçlu sorular olarak da yaz (evet/hayır ile yanıtlanacak biçimde sorma). Kişi
  yanıtlarsa tarifi güncelleyip yeniden kaydet. Tarif işaretli noktalarla onaylanırsa bu noktalar planda VARSAYIM
  olarak yazılır.

## Kesin kural
Onay olmadan uygulama yapılmaz. Tarif, plan ve görevler için kişinin onayı kaydedilmeden hiçbir yazma aracı
çağrılmaz: Revit'e yerleştirme, modeli değiştiren kod ve dosya yazma bu kurala dahildir. Okuma ve inceleme serbesttir.
Tek istisna, iş kaydına verilecek belge taslağının `.aec/taslak/<aşama>.md` dosyasına yazılmasıdır; bu klasöre başka
bir şey yazılmaz (SKILL.md, "İş kaydı aracı").
"Uygun görünüyor" gibi genel bir onay henüz yazılmamış bir belgeyi onaylamaz; onay yalnızca kaydedilen belgeye ve
yalnızca hook'un kaydettiği "evet" ile verilir.

## Kaçınılacak düşünceler
| Düşünce | Gerçek |
|---|---|
| "Seçenek sunarsam kişinin işini kolaylaştırırım." | Seçenek yönlendirir; önce kişinin anlatmasını iste. |
| "Makul varsayılanları kendim doldururum." | Doldur, ama VARSAYIM diye yaz. Kişi duymadığı bir varsayımı reddedemez. |
| "İş küçük, görüşmeye gerek yok." | Sınıfı kural belirler; küçük bir model değişikliği de bu yoldan geçer, belgeler kısa tutulur. |
| "Kişi 'olur' dedi." | Onay yalnızca kaydedilen belgeye, kaydedilen "evet" ile verilir. |

---
Uyarlanmıştır: obra/superpowers, `brainstorming` skill'i (MIT lisansı).
