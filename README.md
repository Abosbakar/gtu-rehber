# GTÜ Rehber

> 🎬 **Demo videosu:** https://youtu.be/N1kTIqeYYLw

GTÜ öğrencilerinin akademik sorularına yönetmeliğe, akademik takvime ve diğer öğrencilerin deneyimlerine dayanarak cevap veren yerel yapay zekâ asistanı. Gerekli dilekçeyi de doldurulmuş PDF olarak hazırlar. İnternetteki hiçbir yapay zekâ servisine bağlanmaz; her şey kendi bilgisayarınızda, Docker içinde ve sadece işlemciyle (CPU) çalışır.

## Problem

Öğrenci hastalanıp sınava giremediğinde, notuna itiraz etmek ya da kaydını dondurmak istediğinde üç soruya cevap arar:

1. **Hangi kural geçerli?** Bilgi onlarca yönetmelik ve yönergeye dağılmış durumda.
2. **Son gün ne zaman?** Süreler "5 iş günü" gibi yazılıyor; hafta sonları ve resmi tatiller hesaba katılmalı. Süreyi kaçırmak hak kaybı demek.
3. **Ne yapmalıyım?** Hangi belge gerekli, dilekçe nasıl yazılır, kime verilir?

Bu soruların cevabı genelde koridorda, kulaktan kulağa öğreniliyor.

## Çözüm

Öğrenci durumunu kendi cümlesiyle yazar: _"Hastalandım, Pazartesi AERO408 vizesine giremedim"_. GTÜ Rehber şunları yapar:

1. **Durumu anlar:** Mesajı 21 konudan birine atar; ders kodunu (AERO408), mazereti (sağlık sorunu) ve tarihi (Pazartesi) çıkarır. Tanımadığı bir durumda _"emin değilim, öğrenci işlerine danışın"_ der.
2. **Kuralı gösterir:** 34 resmî belgedeki 669 madde arasından ilgili maddeyi bulur ve tam metniyle gösterir (Madde 29 – Mazeret sınavı).
3. **Son günü hesaplar:** Akademik takvimdeki resmi tatilleri atlayarak iş günü sayar: _"Son başvuru gününüz 26 Ekim 2026 Pazartesi (1 iş günü kaldı)."_
4. **Deneyimleri ekler:** Benzer durumu yaşamış öğrencilerin, yönetici onayından geçmiş deneyimlerini **"resmi değil"** etiketiyle gösterir.
5. **Dilekçeyi hazırlar:** Gerekli belgeleri listeler; ders kodu, tarih ve mazeret önceden doldurulmuş dilekçeyi PDF olarak verir.
6. **Deneyim toplar:** Öğrenci kendi deneyimini paylaşabilir. Kişi adları kayıttan önce silinip rollere çevrilir ("bölüm staj komisyonu üyesi" gibi). Paylaşım yönetici onayından sonra yayınlanır; "Ben de yaşadım" sayacı tutulur.

### Kapsam

| Seviye | Konular | Asistan ne verir |
|---|---|---|
| **Tam destek** | Mazeret sınavı, ders ekle-bırak, kayıt dondurma, staj başvurusu, not itirazı | Madde + son başvuru günü + deneyimler + belge listesi + doldurulmuş dilekçe PDF |
| **Bilgi desteği** | Yatay/dikey geçiş, çift anadal, yandal, yaz okulu, ders muafiyeti ve intibak, muafiyet sınavı, İngilizce hazırlık, Erasmus, azami süre ve ek sınav, mezuniyet ve diploma, KYK burs/kredi, kısmi zamanlı çalışma, engelli öğrenci sınav düzenlemeleri, akademik danışmanlık, psikolojik danışmanlık | Madde + akademik takvimde varsa tarih + deneyimler |

Staj sorularında öğrencinin bölümüne özel staj esasları kullanılır. Kayıt dondurmada KYK burs/kredisinin etkilenebileceği ayrıca hatırlatılır. Tüm kaynakların listesi: [`data/KAYNAKLAR.md`](data/KAYNAKLAR.md).

## Çalıştırma

**Gerekenler:** [Docker Desktop](https://www.docker.com/products/docker-desktop/), en az 8 GB RAM ve yaklaşık 5 GB boş disk. İlk derlemede internet gerekir; yapay zekâ modeli (~1,1 GB) bu sırada Hugging Face'ten otomatik iner. Ekran kartı (GPU) gerekmez.

```bash
git clone https://github.com/Abosbakar/gtu-rehber.git
cd gtu-rehber
docker compose up --build
```

Başka hiçbir adım gerekmez. İlk derleme internet hızına göre 5–15 dakika sürer, sonraki açılışlar birkaç saniyedir. Terminalde `Application startup complete` yazısı göründüğünde uygulama hazırdır.

| Adres | Ne var |
|---|---|
| **http://localhost:3000** | Uygulama (öğrenci ekranı) |
| **http://localhost:3000/admin** | Yönetici sayfası (deneyim onayı) |
| http://localhost:8000 | API |
| http://localhost:8000/health | API sağlık durumu |
| http://localhost:8000/docs | API'nin otomatik belgesi |

### Yönetici anahtarı

Yönetici sayfası `ADMIN_KEY` ile korunur. Depoya şifre yazılmadığı için iki seçenek var:

- **Hiçbir şey yapmazsanız:** Uygulama her açılışta rastgele bir anahtar üretir ve günlüğe yazar. Görmek için:
  ```bash
  docker compose logs backend | findstr anahtar
  ```
  (macOS/Linux'ta `findstr` yerine `grep`.)
- **Kalıcı anahtar için:** `.env.example` dosyasını `.env` adıyla kopyalayıp `ADMIN_KEY` değerini değiştirin. Port, model ve CORS ayarları da bu dosyadan okunur.

### Durdurma

```bash
docker compose down
```

Öğrenci deneyimleri Docker volume'unda saklanır ve kapatıp açınca kaybolmaz. Veritabanını da silmek için: `docker compose down -v`.

### Sorun çıkarsa

| Belirti | Çözüm |
|---|---|
| `port is already allocated` | 3000 ya da 8000 portu dolu. `.env` dosyasında `FRONTEND_PORT` / `BACKEND_PORT` değerlerini değiştirin. Ön yüz portunu değiştirirseniz `CORS_ORIGINS` değerini de güncelleyin. |
| Sayfada "Sunucuya ulaşılamıyor" | Arka uç açılırken belgeleri ~10 saniye indeksler; biraz bekleyin. |
| `docker` komutu bağlanamıyor | Docker Desktop açık değil; açıp yeşil "Engine running" yazısını bekleyin. |
| Cevaplar uzun sürüyor | `.env` dosyasında `LLM_THREADS` değerini işlemci çekirdek sayınıza göre ayarlayın (0 = otomatik). |

## Mimari

```
 Tarayıcı ──► frontend (nginx, :3000) ── derlenmiş React uygulaması
    │
    └──── HTTP/JSON ──► backend (FastAPI, :8000)
                          ├─ Konu belirleme ─── anahtar kelimeler + yerel Qwen modeli
                          ├─ Madde arama ────── BM25, 34 PDF / 669 madde
                          ├─ Süre hesabı ────── akademik takvim + iş günü (Python)
                          ├─ Deneyimler ─────── SQLite (Docker volume) + anonimleştirme
                          └─ Dilekçe ────────── şablon + reportlab (DejaVu fontu)
```

| Parça | Teknoloji |
|---|---|
| `frontend/` | React 18 + Vite; nginx ile derlenmiş halde sunulur, geliştirme sunucusu kullanılmaz |
| `backend/` | Python 3.11, FastAPI; `/health`, `/ask`, `/experiences`, `/petition`, `/admin/...` |
| Dil modeli | Qwen2.5-1.5B-Instruct (GGUF, Q4_K_M), llama-cpp-python hazır CPU wheel'i ile; derleme sırasında otomatik iner |
| Arama | BM25 (Türkçe karakter sadeleştirme ve 5 harfli kök ile, elle yazıldı) |
| Veritabanı | SQLite |
| Dilekçe | reportlab, Türkçe karakterler için DejaVu fontu |

### Yapay zekâ nerede kullanılıyor, nerede kullanılmıyor?

Küçük bir dil modeli serbest metin yazarken kural uydurabiliyor (geliştirme sırasında bunu yaşadık, aşağıda anlatıyoruz). Bu yüzden görevler bilinçli olarak bölündü:

| İş | Kim yapıyor |
|---|---|
| Mesajın hangi konuya ait olduğu | Önce anahtar kelimeler; net değilse **yerel dil modeli** (cevabı dilbilgisi kısıtıyla sadece geçerli konu kodlarından biri olabilir) |
| Mazeret nedeni, deneyimlerdeki kişi adları | Önce kurallar; kalanlar için **yerel dil modeli** |
| Cevabın kişiye özel giriş cümlesi | **Yerel dil modeli** (rakam, madde numarası veya "ben" ağzından ifade içerirse otomatik reddedilir) |
| Yönetmelik maddesi | Arama (BM25); metin olduğu gibi gösterilir |
| Son başvuru günü | Python kodu (akademik takvim + resmi tatiller) |
| Dilekçe metni | Sabit şablon |

## Gizlilik ve güvenlik

- Hiçbir bulut yapay zekâ servisi (Claude, OpenAI, Gemini vb.) çağrılmaz; model konteynerin içinde çalışır.
- Deneyimlerdeki kişi adları, telefon, e-posta ve öğrenci numaraları kayıttan önce silinir; paylaşımlar yönetici onayı olmadan görünmez.
- Dilekçe için girilen ad ve öğrenci numarası hiçbir yere kaydedilmez ve günlüğe yazılmaz.
- Şifreler depoda yoktur; `.env` dosyası `.gitignore` içindedir, depoda sadece `.env.example` bulunur.
- Debug modu kapalıdır; hatalı girdiler uygulamayı çökertmez, Türkçe hata mesajı döner.

## Sınırlamalar

- GTÜ Rehber resmî bir kaynak değildir; her cevapta bilgilerin bölümle doğrulanması hatırlatılır.
- Belgeler 24 Ekim 2026'da indirildi. Yönetmelik değişirse `data/` klasörünün güncellenmesi gerekir.
- Staj başvuru tarihleri bölümlere göre değiştiği için staj konusunda kesin son gün hesaplanmaz.
- Anonimleştirme her adı yakalayamayabilir; bu yüzden yönetici onayı zorunludur.

## Testler

Arka uçta 52 otomatik test bulunur: madde arama, konu belirleme, tarih ve süre hesabı, anonimleştirme, API ve dilekçe.

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install fastapi==0.115.6 uvicorn==0.32.1 pydantic-settings==2.7.0 pypdf==5.1.0 reportlab==4.2.5 httpx pytest
.venv/Scripts/python -m pytest
```

(macOS/Linux'ta `.venv/Scripts/` yerine `.venv/bin/`. Dil modeli testlerde kullanılmaz.)

## Klasör yapısı

```
backend/          FastAPI arka uç (app/), testler (tests/), model indirme ve takvim betikleri (scripts/)
frontend/         React + Vite ön yüz, nginx yapılandırması
data/             34 resmî belge (PDF), akademik takvim (JSON) ve kaynak listesi
docs/             Geliştirme notları ve demo video senaryosu
docker-compose.yml
.env.example
```

## Geliştirici

- **Abdullah Bakar** – GTÜ "Claude's Plan" yapay zekâ yarışması, bireysel katılım

## Yapay zekâyı nasıl kullandık

**Araç:** Claude Code (Claude masaüstü uygulaması, Claude Opus 5.5 modeli). Claude ürünün parçası değil, sadece geliştirme aracı olarak kullanıldı.

**Nasıl çalıştık:** Kodlama bilgim olmadığı için kodun tamamını Claude Code yazdı. Benim rolüm projeyi tasarlamak, her adımı onaylamak, uygulamayı kullanıp test etmek ve kararları vermekti. Proje 4 güne bölündü (24–27 Ekim). Her gün sadece o günün işi yapıldı, her commit'ten önce ne yapılacağı bana söylendi. Gün sonlarında karşılaştığımız sorunlar [`docs/gelistirme-notlari.md`](docs/gelistirme-notlari.md) dosyasına yazıldı. Bu bölüm o notlardan derlendi.

**Hangi işlerde kullandık?**

| İş | Claude Code ne yaptı |
|---|---|
| Planlama | Şartnameyi okuyup her maddeyi plana bağladı; 5 gün şartı ile 4 günlük plan arasındaki farkı yakaladı. |
| Veri toplama | GTÜ, YÖK ve KYK belgelerini resmî sitelerden buldu ve indirdi. Her PDF'in okunabildiğini kontrol etti, eski ya da yürürlükten kalkmış belgeleri ayıkladı. |
| Kod | Arka uç, ön yüz, Docker yapılandırması, testler. |
| Hata ayıklama | Docker/WSL kurulumu, ağdaki güvenlik duvarı, karışık karakter kodlaması gibi sorunları teşhis etti. |
| Test | 52 otomatik test yazdı; uygulamayı tarayıcıda uçtan uca kullanarak denedi. |

**Kullandığımız istem örnekleri:**

- Başlangıç: _"Bu klasör GTÜ yarışması için projem… sartname.pdf dosyasını oku ve her şartı uygula… LLM sadece sınıflandırma, bilgi çıkarma ve kısa cevap yazımı için kullanılsın; madde metni aramadan, süre koddan, dilekçe şablondan gelsin."_
- Günlük: _"Gün 2'ye başlıyoruz"_, _"Bugün son gün"_
- Kapsam kararı: _"Kapsama ekle o zaman, bunlar öğrenci için önemli sorular."_
- Sorgulama: _"Daha fazla belge yüklememizin problemi ne olur, açıklar mısın?"_, _"Yönetici onayı nasıl olacak, bu soruyu kasteden sorularda bu bilgi çıkacak mı?"_

**Benim verdiğim kararlar ve yönlendirmeler:**

- **Kapsamı genişlettim.** İlk planda 5 durum vardı. GTÜ yönerge sayfasındaki diğer konuların da öğrenciler için önemli olduğunu söyleyip genişletilmesini istedim. Claude Code bunun arama kalitesini düşürebileceği konusunda uyardı; birlikte "tam destek" ve "bilgi desteği" olarak iki seviyeli bir yapıya karar verdik.
- **Bilgiler az geldi dedim.** Bunun üzerine daha fazla belge eklemenin riskleri (yanlış madde, çelişen kurallar) konuşuldu ve belgeler tek tek konulara bağlandı.
- **Deneyimlerin eşleşmesini sorguladım.** Bir uçak mühendisliği deneyiminin bilgisayar mühendisliği sorusunda da çıkacağını fark edince, deneyimler soruya benzerliğe göre sıralanmaya başlandı.
- **Kurulumu kendim yaptım.** Docker Desktop, WSL ve Windows sanallaştırma ayarlarını yönetici yetkisiyle kendim kurdum. Claude Code sistem ayarlarını kendisi değiştirmedi, adımları anlattı.

**Yapay zekânın hataları ve nasıl düzeltildi:**

- **Ürünün içindeki küçük model kural uydurdu (en önemli ders).** İlk sürümde cevapları Qwen modeli yazıyordu. Testlerde yaz okulu sorusunda yönetmeliğin tersini söyledi, KYK sorusunda olmayan bir kural yazdı, staj cevabında yanlış madde numarası verdi. Öğrenciye yanlış kural söylemek hiç cevap vermemekten kötü olduğu için tasarım değişti: kurallar ve tarihler koddan geliyor, model sadece tek cümlelik giriş yazıyor. Bu sayede cevap süresi de 16 saniyeden 1–3 saniyeye indi.
- **Claude Code yanlış madde numarası yazdı.** "D sınavının mazeret sınavı yoktur" notuna Madde 26 yazmıştı. Metinden doğrulayınca doğrusunun Madde 25 olduğu görüldü ve düzeltildi.
- **Kendi yazdığı kodda hatalar yaptı.** Dosyaları otomatik düzenlerken kaçış karakterlerini bozup sözdizimi hatası oluşturdu. Ön yüz Dockerfile'ında bir ayar dosyasını kopyalamayı unuttu, bu yüzden derleme "vite bulunamadı" hatası verdi. İkisi de testler ve derleme kontrolüyle hemen yakalandı.
- **Ortam sorunlarını teşhis etti.** Bulunduğumuz ağdaki bir güvenlik duvarı npm ve Debian paket sunucularını engelliyordu. Claude Code sertifika zincirini inceleyip nedeni buldu. Sertifika kontrolünü kapatmak yerine güvenli bir yol seçti: npm'in resmî aynası ve Alpine tabanlı imaj.
- **Ayrıntıları test ederek iyileştirdi.** Anonimleştirmede "Danışmanım Ali Bey" ifadesindeki "Danışmanım" kelimesinin de silinmesi, dilekçede "arz ederim" kelimesinin iki kez geçmesi, GTÜ takvim sayfasındaki karışık karakter kodlaması gibi sorunlar tek tek yakalanıp testle güvenceye alındı.

**Öğrendiğimiz:** Yapay zekâ asistanı, kod yazmanın yanında "neden böyle yapıyoruz?" sorusunu tartışmak için de çok faydalı oldu. Ama hem ürünün içindeki modelin hem de geliştirme asistanının hata yapabildiğini gördük. Her adımı test etmek ve resmî kaynakla doğrulamak bu yüzden şart.
