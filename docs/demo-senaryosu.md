# Demo Video Senaryosu (~3 dakika)

Şartname, uygulamanın Docker ile ayağa kalktığının ve çalışırken ekranda gösterildiği, sesi anlaşılır bir ekran kaydı istiyor. Kayıt 720p, yaklaşık 3 dakika olmalı. YouTube'a **liste dışı** yüklenip bağlantısı README'nin en üstüne eklenecek.

## Kayıttan önce (videoda görünmez)

1. Docker Desktop'ı açın ve sol altta yeşil "Engine running" yazısını bekleyin.
2. Proje klasöründe `.env.example` dosyasını kopyalayıp adını `.env` yapın. `ADMIN_KEY=` satırına kendinizin bildiği bir anahtar yazın. Bu dosyayı videoda **göstermeyin**.
3. PowerShell'i proje klasöründe açın ve bir kez çalıştırın:
   ```bash
   docker compose down
   ```
4. Tarayıcıda iki sekme hazırlayın: `http://localhost:3000` ve `http://localhost:3000/admin`. Henüz yenilemeyin.
5. Paylaşacağınız deneyim cümlesini bir not defterine yazın, kayıt sırasında yapıştırın. Örnek:
   _"Raporumu e-Nabız çıktısıyla teslim ettim, bölüm sekreterliği aynı gün kabul etti. Hocamın adını sorarlarsa ders koordinatörü Prof. Dr. Ayşe Yılmaz diye yazmıştım."_
   Bu cümledeki isim kayıt sırasında otomatik silinecek; videoda bunu göstermek etkileyici olur. Gerçek bir hocanın adını yazmayın.
6. Bildirimleri kapatın (Windows: Odaklanma / Rahatsız Etmeyin). Kayıt için `Win + Alt + R` kullanacaksınız. Mikrofonun açık olduğundan emin olun.

## Akış

| Süre | Ekranda | Söyleyeceğiniz |
|---|---|---|
| 0:00–0:20 | PowerShell. `docker compose up --build` yazıp Enter'a basın. | "Merhaba, ben Abdullah Bakar. Projem GTÜ Rehber: öğrencinin derdini dinleyip yönetmeliğe ve akademik takvime göre ne yapması gerektiğini söyleyen, dilekçesini de hazırlayan bir asistan. Tüm uygulama tek komutla Docker'da ayağa kalkıyor. Yapay zekâ modeli de bilgisayarın içinde, sadece işlemciyle çalışıyor; hiçbir bulut servisine bağlanmıyor." |
| 0:20–0:35 | "Application startup complete" yazısı görününce tarayıcıda `localhost:3000` sekmesini yenileyin. | "Arka uç 34 resmî belgeyi, yani GTÜ yönetmeliğini, staj yönergelerini, akademik takvimi, YÖK ve KYK yönetmeliklerini okudu ve 669 maddeyi indeksledi." |
| 0:35–1:05 | "Hastalandım, Pazartesi AERO408 vizesine giremedim" örneğine tıklayın. Yükleniyor göstergesini, sonra cevabı gösterin. Son başvuru günü kartının üzerinde durun. | "Kendi cümlemle yazıyorum. Sistem bunun bir mazeret sınavı durumu olduğunu anladı, ders kodunu ve mazereti çıkardı. Yönetmelikteki Madde 29'u buldu. Son başvuru gününü de akademik takvimdeki resmi tatilleri atlayarak iş günü hesabıyla buldu. Kuralları ve tarihleri yapay zekâ uydurmuyor, koddan ve resmî metinden geliyor." |
| 1:05–1:20 | Aşağı kaydırıp "Yönetmelikteki ilgili maddeler" kartını açın. | "Maddenin tam metni de burada; öğrenci kaynağı kendi gözüyle görebiliyor." |
| 1:20–1:45 | "Dilekçemi hazırla" bölümünü açın. Ders kodu ve mazeretin dolu geldiğini gösterin. Ad, numara ve bölümü yazıp "PDF indir"e basın, ardından indirilen PDF'i açın. | "Gerekli belgeler listeleniyor ve dilekçe hazır geliyor: ders kodu ve mazeret sohbetten otomatik dolduruldu. Türkçe karakterli, yönetmelik maddesine atıf yapan bir PDF. Girdiğim kişisel bilgiler hiçbir yere kaydedilmiyor." |
| 1:45–2:10 | Uygulamaya dönüp "Deneyiminizi paylaşın"ı açın, hazırladığınız cümleyi yapıştırıp "Paylaş"a basın. Kaydedilen haldeki "[…]" kısmını gösterin. | "Öğrenciler kendi deneyimlerini de paylaşabiliyor. Yazdığım cümledeki hoca adı kayıttan önce otomatik silinip bir role çevrildi. Paylaşım yönetici onayına gidiyor." |
| 2:10–2:30 | `/admin` sekmesine geçin, anahtarı girin, deneyimi "Onayla"yın. | "Yönetici sayfasından onaylıyorum. Anahtar .env dosyasından okunuyor, depoda şifre yok." |
| 2:30–2:50 | Ana sekmeye dönüp aynı soruyu tekrar sorun. "Resmi değil – öğrenci deneyimi" etiketli kartı gösterip "Ben de yaşadım"a basın. | "Aynı soruyu tekrar soruyorum: deneyim artık 'resmi değil' etiketiyle cevapta görünüyor. Diğer öğrenciler 'ben de yaşadım' diyerek doğrulayabiliyor." |
| 2:50–3:00 | (İsteğe bağlı) "Kantinde yemek ne?" yazın. | "Tanımadığı bir soruda uydurmuyor, öğrenci işlerine yönlendiriyor. Teşekkürler." |

## Kayıttan sonra

1. Kaydı izleyin; ses anlaşılır mı, `.env` ya da anahtar ekranda görünmüş mü kontrol edin.
2. YouTube'a yükleyin. Görünürlüğü **Liste dışı** seçin.
3. Bağlantıyı Claude Code'a verin; README'nin en üstüne eklenip "Demo videosu bağlantısı README'ye eklendi" mesajıyla commit atılacak.

## Bir şey ters giderse

- **Cevap gelmiyor ya da "Sunucuya ulaşılamıyor" yazıyor:** Arka uç belgeleri indekslerken ~10 saniye bekleyin ve sayfayı yenileyin.
- **Yönetici anahtarı kabul edilmiyor:** `.env` dosyasını değiştirdikten sonra `docker compose up --build` ile yeniden başlatmak gerekir.
- **Kayıt bozuldu:** Sorun değil, sadece o kısmı tekrar çekip birleştirebilir ya da baştan kaydedebilirsiniz.
