# Geliştirme Notları

Bu dosya, README'deki "Yapay zekâyı nasıl kullandık" bölümü için geliştirme sırasında karşılaşılan sorunları ve verilen kararları kayıt altına alır.

**Kullanılan araç:** Claude Code (masaüstü uygulaması). Kodun tamamı Claude Code tarafından yazılıyor; her adım ve her commit geliştirici tarafından onaylanıyor.

## Gün 1 – 24 Ekim 2026

**Yapılanlar**
- Şartname PDF'i Claude Code'a okutuldu ve maddeleri proje planıyla karşılaştırıldı.
- Proje iskeleti oluşturuldu: README taslağı, `.gitignore`, `.env.example`, `backend/`, `frontend/`, `data/`, `docs/` klasörleri.
- İlk commit atıldı: "Proje iskeleti ve README taslağı eklendi".
- GTÜ yönetmelik, staj yönergesi ve akademik takvim kaynakları web aramasıyla bulundu.

**Karşılaşılan sorunlar ve çözümler**
- **Şartname dosyasının adı yanlıştı:** Dosya `sartname.pdf` yerine `sartname.pdf.pdf` olarak kaydedilmişti (Windows uzantıyı gizlediği için çift uzantı oluşmuş). `.gitignore`'a iki ad da eklendi.
- **`.env.example` klasörde yoktu:** Hazır olduğu düşünülüyordu ama klasörde bulunmuyordu. Claude Code şartnameye uygun şekilde (port, model yolu, veritabanı yolu, ADMIN_KEY, debug kapalı) sıfırdan oluşturdu.
- **Plan PDF'i de klasördeydi:** Kişisel çalışma planı PDF'i depoya girmesin diye `.gitignore`'a eklendi.
- **Boş klasörler Git'e girmiyor:** Git boş klasörleri takip etmediği için her klasöre `.gitkeep` dosyası kondu.
- **Şartname ile plan arasında gün farkı:** Şartname commit'lerin en az 5 güne yayılmasını istiyor, proje 4 güne planlandı. Organizatörden 4 gün için onay alındığı not edildi.
- **PDF okuma aracı eksikti:** Python'da `pypdf` kurulu değildi; Claude Code bunun yerine sistemde bulunan `pdftotext` aracını kullandı.
- **2026–2027 akademik takvim PDF olarak bulunamadı:** GTÜ'nün resmi takvim sayfasında yalnızca 2025–2026 ve öncesi için PDF var; 2026–2027 takvimi sayfanın içinde tablo olarak duruyor. Claude Code sayfayı Microsoft Edge'in başsız (headless) modu ile PDF'e çevirdi (`data/akademik-takvim-2026-2027.pdf`).
- **Yönetmelik linki kırıktı:** Web aramasında çıkan R6 sürümünün adresi 404 (bulunamadı) hatası verdi. İkinci aramada daha yeni R7 sürümü (01.10.2024) bulundu ve o indirildi (`data/yonetmelik.pdf`).
- **İndirilen dosyalar doğrulandı:** Bir indirme PDF yerine hata sayfası (HTML) döndürmüştü; Claude Code dosya türünü kontrol edince fark etti. Sonunda üç PDF'in de metni çıkarılıp Türkçe karakterlerin ve ilgili maddelerin (Madde 28 not itirazı, Madde 29 mazeret sınavı) okunabildiği kontrol edildi.
- **Staj yönergesi fakülteye göre değişiyor:** Birden fazla staj yönergesi var. AERO408 örneği Mühendislik Fakültesi'ne ait olduğu için Mühendislik Fakültesi Staj Yönergesi (YÖ-0019) seçildi.
