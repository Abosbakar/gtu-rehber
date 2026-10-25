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
- **Kapsam genişletildi (geliştiricinin kararı):** İlk planda 5 durum vardı. Geliştirici, GTÜ yönerge sayfasındaki diğer belgelerin de öğrenciler için önemli olduğunu belirterek kapsamın genişletilmesini istedi. Claude Code önce bunun arama kalitesini düşürebileceği uyarısını yaptı, karar sonrası şu yolu önerdi: 5 durum "tam destek" (dilekçe + süre hesabı) olarak kalıyor, diğer 16 konu "bilgi desteği" (madde + tarih) olarak ekleniyor. Lisansüstü, personel ve araştırma merkezi yönergeleri gibi öğrenciyle ilgisiz belgeler bilerek dışarıda bırakıldı.
- **mevzuat.gov.tr komut satırından aranamadı:** YÖK ve KYK yönetmeliklerinin numaraları tahminle bulunamadı (404). Claude Code uygulama içi tarayıcıda sitenin arama formunu kullanarak doğru numaraları buldu (13948, 40390, 40391), PDF'leri ise doğrudan indirdi.
- **Eski/yürürlükten kalkmış belgeler ayıklandı:** 2017 öncesi girişliler için olan eski yönetmelik (YN-0009) ve 2023'te kaldırılan YÖK Öğrenci Disiplin Yönetmeliği, yanlış bilgi vermemek için eklenmedi.
- **Bazı staj esaslarında "MADDE" başlığı yok:** Bölüm staj esaslarının bir kısmı numaralı başlıklarla yazılmış. Gün 2'de metni parçalara bölerken bu belgeler için başlık tabanlı bölme gerekecek.
- **Staj yönergesi fakülteye göre değişiyor:** Birden fazla staj yönergesi var. İlk aşamada yalnızca Mühendislik Fakültesi Staj Yönergesi (YÖ-0019) seçilmişti. Kapsam genişletilince tüm fakültelerin staj yönergeleri ve mühendislik bölümlerinin staj uygulama esasları eklendi; AERO408 örneği için Havacılık ve Uzay Bilimleri Fakültesi yönergesi (YÖ-0089) de bulundu.

## Gün 2 – 25 Ekim 2026

**Yapılanlar**
- FastAPI arka uç, `/health` ve `/ask` uç noktaları; tüm ayarlar ortam değişkenlerinden okunuyor.
- 34 belgeyi maddelere bölen ve BM25 ile arayan modül (BM25 dış kütüphane yerine ~40 satırda elle yazıldı).
- Yerel Qwen2.5-1.5B modeli Docker derlemesi sırasında Hugging Face'ten iniyor; konu belirleme, bilgi çıkarma ve kısa giriş cümlesi için kullanılıyor.
- Akademik takvimden iş günü ve başvuru penceresine göre son başvuru günü hesabı; SQLite deneyim veritabanı.
- 35 otomatik test (arama, konu belirleme, tarih hesabı, veritabanı).

**Karşılaşılan sorunlar ve çözümler**
- **Docker çalışmıyordu:** Windows'ta "Virtual Machine Platform" özelliği kapalıydı. Claude Code BIOS'ta sanallaştırmanın açık olduğunu kontrol etti, geliştirici yönetici PowerShell'de iki `dism` komutunu çalıştırıp bilgisayarı yeniden başlattı. `wsl --update` sunucuya bağlanamadı ama WSL zaten güncel olduğu için gerek kalmadı.
- **Hazır llama-cpp-python wheel'leri Debian'da çalışmadı:** CPU wheel'leri Alpine (musl) için derlenmişti; `python:3.11-slim` imajında `libc.musl` hatası verdi. Ayrıca Docker içinden Debian paket sunucusu 403 döndürüyordu. Çözüm: arka uç imajı `python:3.11-alpine` tabanına taşındı; derleme gerekmeden kuruldu.
- **Ham arama yanlış maddeleri getiriyordu:** "Hastalandım, vizeye giremedim" cümlesinde yönetmelikteki "mazeret" kelimesi geçmediği için arama staj sigortası maddelerini buluyordu. Çözüm: önce konu belirleniyor, sonra arama sadece o konunun belgelerinde ve konuya özel resmi ifadelerle yapılıyor.
- **Madde başlıkları kayıyordu:** Parantezle biten başlıklar ("Yarıyıl izni (kayıt dondurma)") önceki maddenin sonuna yapışıyordu; testlerle yakalanıp düzeltildi.
- **Madde numarası doğrulandı:** Claude Code "D sınavının mazeret sınavı yoktur" notuna önce Madde 26 yazmıştı; metinden kontrol edince doğrusunun Madde 25 olduğu görüldü ve düzeltildi.
- **Küçük dil modeli serbest metinde güvenilmezdi (en önemli karar):** İlk denemede model cevapları tekrar ediyor, liste yapıyor, öğrencinin ağzından konuşuyordu. Örnek cevap (few-shot) ve tekrar cezası eklenince düzeldi ama bu kez kural uydurdu: yaz okulu sorusunda yönetmeliğin tersini söyledi, KYK sorusunda olmayan bir kural yazdı, staj cevabında yanlış madde numarası verdi. Karar: kurallar ve maddeler her zaman koddan/aramadan geliyor; model sadece kişiye özel tek cümlelik bir giriş yazıyor. Bu cümlede rakam, madde numarası veya "ben" ağzından ifade varsa otomatik reddediliyor. "Geçmiş olsun / Başınız sağ olsun" ifadesini de model değil, mesajdaki kelimelere bakan kod seçiyor.
- **Yavaşlık:** Cevaplar ilk başta 10–16 saniye sürüyordu. Model çekirdek sayısını otomatik seçecek şekilde ayarlanıp (`LLM_THREADS=0`) model çıktısı tek cümleye indirilince süre 1–3 saniyeye düştü.
- **Takvim sayfasında karışık karakter kodlaması:** GTÜ'nün takvim sayfasında bazı hücreler Windows-1254, bazıları UTF-8 ile yazılmış; "Ağustos" gibi aylar okunamıyor, "14 Eylül–02 Ekim" yanlış yıla düşüyordu. Her hücre kendi kodlamasıyla çözülerek düzeltildi; "Yeni Yıl Tatili" ve "ﬁ" bitişik harfi de ayrıca ele alındı.
- **Claude Code'un kendi hataları:** Dosyaları komut satırından otomatik düzenlerken iki kez kaçış karakterlerini (`\n`, `\b`) bozup sözdizimi hatasına yol açtı; testler ve derleme kontrolüyle hemen fark edilip düzeltildi.
