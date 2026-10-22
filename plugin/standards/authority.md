# Ofis kuralları (aec)
Yetki sırası, çelişkide üstteki kazanır:
1. Çizim (DWG/DXF): ölçüler yalnızca araçla okunur, görselden ölçü alınmaz.
2. Proje kuralları: projenin AGENTS.md/CLAUDE.md dosyası ve .aec/ klasörü.
3. Ofis standartları: bu plugin.
4. Araştırma kataloğu: yalnızca öneri; kullanıcı onaylamadan modele girmez.
Revit'e yazmadan önce açık belgenin dosya yolunu .aec/proje.md'deki kopya yoluyla karşılaştır (başlık yetmez; MD yoksa ya da yollar tutmuyorsa dur ve sor), planı göster, onay al. Yazdıktan sonra Revit okuma araçlarıyla geri oku; bu okuma aec:dogrulayici raporunun yerine geçmez. Kendi yazdığın bir kontrol dosyasına bakıp "geçti" deme.
Az sor, çok göster: önce projenin CLAUDE.md ve .aec/proje.md dosyasını oku; eksik kalan en kritik bilgiler için en fazla 3 soru sor; geri kalanı VARSAYIM diye plana yaz; planı göster, onay al, sonra uygula.
Karmaşık işte (çizim/model) tam görüşme yapılır; 3 soru sınırı uygulanmaz.
Kendi işini onaylama: onay ve kabul kişiden gelir, kontrol bağımsız kontrolcü aec:dogrulayici ile yapılır.
