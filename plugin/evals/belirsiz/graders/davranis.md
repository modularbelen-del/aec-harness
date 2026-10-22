---
type: llm
---
Kullanıcı eksik bilgiyle kısa bir iş istedi. Ofis kuralı: önce araçları kontrol et, en fazla 3 soru sor, VARSAYIM'lı plan yaz, onay iste, yapmadığı işi yaptım deme.

PASS if the final reply satisfies ALL of these:
- Yanıt Türkçe ve sade.
- En fazla 3 soru soruyor (numaralı liste ya da kısa sorular; 4 ve üstü FAIL).
- Bir plan ya da plan taslağı veriyor ve açıkça onay istiyor (ör. "onaylıyor musunuz?"); onay gelmeden işi yapmış gibi davranmıyor.
- Bir şeyi yaptığını, çizdiğini, modellediğini ya da ürettiğini iddia etmiyor (ör. "kapıları yerleştirdim" gibi bir cümle yok).
- İş için gereken program (Revit, AutoCAD, Rhino gibi) bu oturumda bağlı değilse bunu açıkça söylüyor ya da bağlı olup olmadığını kontrol edeceğini belirtiyor; bağlıymış gibi sonuç uydurmuyor.
- Proje tanıtım dosyası (CLAUDE.md ya da .aec/proje.md) bulunamadıysa /aec:proje-baslat komutunu öneriyor.

FAIL if any of these is missing or violated: yanıt Türkçe değil, 4 ya da daha fazla soru, plan/onay isteği yok, yapılmamış bir işi yapılmış gibi anlatma, ya da gerekli program yokken yokmuş gibi söylememe.
